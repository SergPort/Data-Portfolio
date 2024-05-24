from Budget import *



app =  run_full_pipeline()

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Run the Dash app
if __name__ == '__main__':
    # Start a timer to open the browser after a short delay
    Timer(1, open_browser).start()
    app.run_server(debug=False)

