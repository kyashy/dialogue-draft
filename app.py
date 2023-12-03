from pathlib import Path

import gradio as gr
import pandas as pd
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
    progress=gr.Progress(track_tqdm=True),
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
        audio=audio_path,
        language=language,
        fp16=False,
        verbose=True,
        initial_prompt=initial_prompt,
    )

    df = create_dataframe(result)
    audio_file_name = Path(audio_path).stem
    output_dir = Path("data/output")
    output_file = output_dir / f"{audio_file_name}.csv"

    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    return df, str(output_file)


def main():
    with gr.Blocks() as demo:
        # Title of the app
        gr.Markdown("# DialogueDraft")
        with gr.Row():
            # Define inputs
            with gr.Column():
                audio_path = gr.Audio(
                    sources=["upload"], type="filepath", label="Audio File"
                )
                with gr.Accordion(label="Advanced Settings", open=False):
                    model_name = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large"],
                        value="large",
                        label="Model",
                    )
                    language = gr.Dropdown(
                        choices=["Japanese", "English", "Auto"],
                        value="Japanese",
                        label="Language",
                    )
                    initial_prompt = gr.Textbox(
                        lines=3,
                        placeholder=(
                            "Optional text to provide as a prompt for the first window. This can be used to provide, or "
                            '"prompt-engineer" a context for transcription, e.g. custom vocabularies or proper nouns '
                            "to make it more likely to predict those word correctly."
                        ),
                        label="Initial Prompt",
                    )
            # Define outputs
            with gr.Column():
                result = gr.Dataframe(label="Result", headers=["start", "end", "text"])
                download = gr.File(label="Download")

        audio_path.upload(
            transcribe_audio,
            inputs=[audio_path, model_name, language, initial_prompt],
            outputs=[result, download],
        )

    # Queue functionality for handling multiple users
    demo.queue()
    demo.launch(server_name="0.0.0.0", show_api=False)


if __name__ == "__main__":
    main()
