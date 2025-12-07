import webview
import os

def start_app():
    # Caminho absoluto para o HTML
    html_path = os.path.abspath("index.html")

    # Cria a janela
    window = webview.create_window(
        title="Random Facts Desktop",
        url=f"file:///{html_path}",
        width=900,
        height=700
    )

    webview.start()

if __name__ == "__main__":
    start_app()