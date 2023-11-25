import pandas as pd
import gradio as gr
import whisper
from whisper.utils import format_timestamp


def create_dataframe(result):
    df = pd.DataFrame.from_dict(result["segments"])
    df["start"] = df["start"].apply(format_timestamp)
    df["end"] = df["end"].apply(format_timestamp)
    return df[["start", "end", "text"]]


def transcribe_audio(
        input_file,
        model_name,
        language,
        initial_prompt,
        progress=gr.Progress(track_tqdm=True)
    ):
    if language == "Auto":
        language = None
    print(f"Loading whisper Model...")
    # If you specify device="cuda:0", 8GB memory will not be enough, so first put it on the CPU.
    model = whisper.load_model(name=model_name, device="cpu")
    # Then move only the model to GPU.
    model.to("cuda:0")
    print(f"Generating Transcript...")
    result = model.transcribe(
        audio=input_file,
        language=language,
        fp16=False,
        verbose=True,
        initial_prompt=initial_prompt,
    )

    df = create_dataframe(result)
    output_file = "data/output/" + input_file.split("/")[-1].split(".")[0] + ".csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    return df, output_file


def main():

    demo = gr.Interface(
        fn=transcribe_audio,
        inputs=[
            gr.Audio(sources=["upload"], type="filepath", label="Audio File"),
            gr.Dropdown(
                choices=["tiny", "base", "small", "medium", "large"],
                value="large",
                label="Model",
            ),
            gr.Dropdown(
                choices=["Japanese", "English", "Auto"],
                value="Japanese",
                label="Language",
            ),
            gr.Textbox(value="議事録を作成します。", label="Initial Prompt"),
        ],
        outputs=[
            gr.Dataframe(label="Result", headers=["start", "end", "text"]),
            gr.File(label="Download"),
        ],
        title="DialogueDraft",
        allow_flagging="never",
    )
    # Queue functionality for handling multiple users
    demo.queue()
    demo.launch()


if __name__ == "__main__":
    main()
