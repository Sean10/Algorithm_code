const vscode = require('vscode');

exports.activate = function() {
    const dec = vscode.window.createTextEditorDecorationType({});
    vscode.window.activeTextEditor.setDecorations(dec, [
        {
            range: new vscode.Range(2, 0, 2, 1),
            renderOptions: {
                after: {
                    contentText: '😀'
                }
            }
        },
        {
            range: new vscode.Range(1, 0, 1, 1),
            renderOptions: {
                after: {
                    contentText: '😀'
                }
            }
        }
    ]);
};