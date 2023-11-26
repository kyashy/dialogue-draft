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
        audio_path,
        model_name,
        language,
        initial_prompt,
        progress=gr.Progress(track_tqdm=True)
    ):
    if audio_path is None:
        raise gr.Error("Please upload your audio file.")
    if language == "Auto":
        language = None
    print(f"Loading whisper Model...")
    # If you specify device="cuda:0", 8GB memory will not be enough, so first put it on the CPU.
    model = whisper.load_model(name=model_name, device="cpu")
    # Then move only the model to GPU.
    model.to("cuda:0")
    print(f"Generating Transcript...")
    result = model.transcribe(
        audio=audio_path,
        language=language,
        fp16=False,
        verbose=True,
        initial_prompt=initial_prompt,
    )

    df = create_dataframe(result)
    output_file = "data/output/" + audio_path.split("/")[-1].split(".")[0] + ".csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    return df, output_file


def main():
    with gr.Blocks() as demo:
        # Title of the app
        gr.Markdown("# DialogueDraft")
        with gr.Row():
            # Define inputs
            with gr.Column():
                audio_path = gr.Audio(
                    sources=["upload"],
                    type="filepath",
                    label="Audio File"
                )
                print(audio_path)
                submit_button = gr.Button("Submit")
                with gr.Accordion(label="Advanced Settings", open=False):
                    model_name = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large"],
                        value="large",
                        label="Model"
                    )
                    language = gr.Dropdown(
                        choices=["Japanese", "English", "Auto"],
                        value="Japanese",
                        label="Language"
                    )
                    initial_prompt = gr.Textbox(
                        label="Initial Prompt",
                    )
            # Define outputs
            with gr.Column():
                result = gr.Dataframe(label="Result", headers=["start", "end", "text"])
                download = gr.File(label="Download")

        submit_button.click(
            transcribe_audio,
            inputs=[audio_path, model_name, language, initial_prompt],
            outputs=[result, download]
        )

    # Queue functionality for handling multiple users
    demo.queue()
    demo.launch()


if __name__ == "__main__":
    main()
