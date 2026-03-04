def outformat(text: str, color: str = '\033[0m') -> str:
    newText = color

    ctrl_matches = {
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
    }

    for c in str(text):
        if c in ctrl_matches.keys():
            newText += '\033[33m' + ctrl_matches[c] + color
        else:
            newText += c

    return newText + '\033[0m'