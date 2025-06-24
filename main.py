from app.app import create_app

app = create_app()

if __name__ == '__main__':
    # 綁定 0.0.0.0 讓其他裝置（例如你的手機）也能連線
    app.run(host='0.0.0.0', port=5000, debug=True)