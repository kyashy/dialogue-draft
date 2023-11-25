import pandas as pd
import gradio as gr
import whisper
from whisper.utils import format_timestamp


def create_dataframe(result):
    df = pd.DataFrame.from_dict(result["segments"])
    df["start"] = df["start"].apply(format_timestamp)
    df["end"] = df["end"].apply(format_timestamp)
    return df[["start", "end", "text"]]


def transcribe_audio(input_file, progress=gr.Progress(track_tqdm=True)):
    print(f"Loading whisper Model...")
    # If you specify device="cuda:0", 8GB memory will not be enough, so first put it on the CPU.
    model = whisper.load_model(name="large", device="cpu")
    # Then move only the model to GPU.
    model.to("cuda:0")
    print(f"Generating Transcript...")
    result = model.transcribe(
        audio=input_file,
        language="Japanese",
        fp16=False,
        verbose=True,
        initial_prompt="議事録を作成します。",
    )

    df = create_dataframe(result)
    output_file = "data/output/" + input_file.split("/")[-1].split(".")[0] + ".csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    return df, output_file


def main():

    demo = gr.Interface(
        fn=transcribe_audio,
        inputs=gr.Audio(sources=["upload"], type="filepath"), 
        outputs=[
            gr.Dataframe(label="Result", headers=["start", "end", "text"]),
            gr.File(label="Download"),
        ],
        title="DialogueDraf",
        allow_flagging="never",
    )
    # Queue functionality for handling multiple users
    demo.queue()
    demo.launch()


if __name__ == "__main__":
    main()
