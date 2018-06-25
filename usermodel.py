@app.route('/', methods=['GET', 'POST'])
def index(result=None):
    if request.args.get('mail', None):
        result = process_text(request.args['mail'])
    return render_template('index.html', result=result)