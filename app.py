from pathlib import Path

import gradio as gr
import pandas as pd
import torch
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
        # Load the language detection model
        print(f"Detecting language...")
        lang_detection_model = whisper.load_model(
            name="base", device="cuda:0", download_root=".cache"
        )
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(lang_detection_model.device)

        # detect the spoken language
        _, probs = lang_detection_model.detect_language(mel)
        language = max(probs, key=probs.get)
        print(f"Detected language: {language}")

        # Free up memory to avoid CUDA out of memory error
        del lang_detection_model
        torch.cuda.empty_cache()

    print(f"Loading whisper Model...")
    # If you specify device="cuda:0", 8GB memory will not be enough, so first put it on the CPU.
    model = whisper.load_model(name=model_name, device="cpu", download_root=".cache")
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

    # Free up memory to avoid CUDA out of memory error
    del model
    torch.cuda.empty_cache()

    return df, str(output_file)


def main():
    with gr.Blocks(title="DialogueDraft") as demo:
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
                        value="medium",
                        label="Model",
                    )
                    language = gr.Dropdown(
                        choices=["Auto", "English", "Japanese"],
                        value="Auto",
                        label="Language",
                    )
                    initial_prompt = gr.Textbox(
                        lines=4,
                        placeholder=(
                            "Optional text to provide as a prompt for the first window. This can be used to provide, or "
                            '"prompt-engineer" a context for transcription, e.g. custom vocabularies or proper nouns '
                            "to make it more likely to predict those word correctly."
                        ),
                        label="Initial Prompt",
                    )
            # Define outputs
            with gr.Column():
                result = gr.Dataframe(
                    label="Result",
                    headers=["start", "end", "text"],
                    wrap=True,
                )
                download = gr.File(label="Download")

        audio_path.upload(
            transcribe_audio,
            inputs=[audio_path, model_name, language, initial_prompt],
            outputs=[result, download],
        )

    # Queue functionality for handling multiple users
    demo.queue()
    demo.launch(server_name="0.0.0.0", share=False, show_api=False)


if __name__ == "__main__":
    main()
