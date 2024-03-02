from flask import Flask, render_template,request
from flask_socketio import SocketIO, join_room, leave_room
import chess
import chess.svg
import time

app = Flask(__name__)
socketio = SocketIO(app)
app.config['STATIC_URL_PATH'] = '/static'
app.config['STATIC_FOLDER'] = 'static'

def display_board(board):
    return chess.svg.board(board=board)

def simple_ai_move(board, is_white):
    legal_moves = list(board.legal_moves)
    return legal_moves[0] if is_white else legal_moves[-1]

def determine_winner(result):
    if result == "1-0":
        return "White wins!"
    elif result == "0-1":
        return "Black wins!"
    else:
        return "It's a draw!"

def play_game(room):
    board = chess.Board()
    frames = []

    while not board.is_game_over():
        white_move = simple_ai_move(board, is_white=True)
        board.push(white_move)
        frames.append({'svg': display_board(board), 'turn': 'Black'})
        socketio.emit('update_board', frames[-1], room=room)
        time.sleep(1)

        if board.is_game_over():
            break

        black_move = simple_ai_move(board, is_white=False)
        board.push(black_move)
        frames.append({'svg': display_board(board), 'turn': 'White'})
        socketio.emit('update_board', frames[-1], room=room)
        time.sleep(1)

    result_message = determine_winner(board.result())
    socketio.emit('game_result', result_message, room=room)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on('start_game')
def handle_start_game():
    room = request.sid 
    join_room(room)
    play_game(room)

@socketio.on('reset_game')
def handle_reset_game():
    room = request.sid
    leave_room(room)
    join_room(room)
    play_game(room)

@socketio.on('pause_resume_game')
def handle_pause_resume_game():
    pass

if __name__ == "__main__":
    socketio.run(app, debug=True)
