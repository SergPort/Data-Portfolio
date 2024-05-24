from Budget import *

vanguard = input("Vanguard Investments: ")
if vanguard == "":
    vanguard = 721
fineco_snp = input("Fineco Investments: ")
if fineco_snp == "":
    fineco_snp = 1964
revolut = input("Revolut Total: ")
if revolut == "":
    revolut = 122
crypto = input("Crypto Investments: ")
if crypto == "":
    crypto = 121

app =  run_full_pipeline(vanguard, fineco_snp, revolut, crypto)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Run the Dash app
if __name__ == '__main__':
    # Start a timer to open the browser after a short delay
    Timer(1, open_browser).start()
    app.run_server(debug=False)

