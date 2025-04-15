// static/js/socket_client.js

document.addEventListener('DOMContentLoaded', function () {
    // Socket.IOサーバーに接続
    var socket = io();
  
    // サーバーからゲーム状態を受信したとき
    socket.on('game_state', function (data) {
      console.log('ゲーム状態を受信:', data);
      updateGameBoard(data.board);
      updateTurnInfo(data.turn);
    });
  
    // マッチング通知を受信したとき
    socket.on('match_found', function (data) {
      console.log('マッチング成立:', data);
      // 例: ルーム情報などを取得して、画面を遷移する処理を実装
    });
  
    // 盤面を更新する関数
    function updateGameBoard(board) {
      var boardDiv = document.getElementById('game-board');
      boardDiv.innerHTML = ''; // 現在の盤面をクリア
      board.forEach(function (row) {
        row.forEach(function (cell) {
          var cellDiv = document.createElement('div');
          if (cell === 1) {
            cellDiv.textContent = '●'; // 黒
          } else if (cell === 2) {
            cellDiv.textContent = '○'; // 白
          }
          boardDiv.appendChild(cellDiv);
        });
      });
    }
  
    // ターン情報を更新する関数
    function updateTurnInfo(turn) {
      var turnInfo = document.getElementById('turn-info');
      turnInfo.textContent = 'ターン: ' + (turn === 1 ? '黒' : '白');
    }
  
    // 盤面のセルがクリックされたときのイベント処理（例）
    document.getElementById('game-board').addEventListener('click', function (event) {
      if (event.target && event.target.nodeName === 'DIV') {
        // クリックされたセルのインデックスから座標を計算（8x8盤面と仮定）
        var index = Array.prototype.indexOf.call(event.currentTarget.children, event.target);
        var x = Math.floor(index / 8);
        var y = index % 8;
        console.log('クリックされたセル:', x, y);
        // サーバーに手の情報を送信する
        socket.emit('make_move', { x: x, y: y });
      }
    });
  });
  