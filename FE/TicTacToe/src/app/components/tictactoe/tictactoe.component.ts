import { Component } from '@angular/core';
import { TicTacToeService } from '../../tic-tac-toe.service';
import { Subject, Subscription, distinctUntilChanged, interval, takeUntil } from 'rxjs';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'tictactoe',
  templateUrl: './tictactoe.component.html',
  styleUrls: ['./tictactoe.component.scss']
})
export class TictactoeComponent {
  grid: number[] = Array(9).fill(0);
  positionDictionary: { [key: string]: number } = {};
  gameBoard: any;
  showOverlay: boolean = true;
  gameStatus: String = 'In progress'
  winner: string = ''
  gameInProgress = true
  displayTimer = false
  trainingStaus = ''
  completed = false
  episodesForm!: FormGroup;
  episodes: number = 0
  gameOver = false

  loading: boolean = false
  isButtonDisabled: boolean = false;
  letsPlay: boolean = false;


  constructor(private gameService: TicTacToeService, private formBuilder: FormBuilder) { }
  private timerSubscription!: Subscription;
  private startTime!: Date;
  public elapsedTime: number = 0;
  public isRunning: boolean = false;

  ngOnDestroy() {
    this.stopTimer();
  }

  startTimer() {
    if (!this.isRunning) {
      this.startTime = new Date();
      this.timerSubscription = interval(10).subscribe(() => {
        const now = new Date();
        this.elapsedTime = now.getTime() - this.startTime?.getTime();
      });
      this.isRunning = true;
    }
  }

  stopTimer() {
    if (this.timerSubscription && !this.timerSubscription.closed) {
      this.timerSubscription.unsubscribe();
      this.isRunning = false;
    }
  }

  resetTimer() {
    this.stopTimer();
    this.elapsedTime = 0;
  }

  formatTime(time: number): string {
    const minutes = Math.floor(time / 60000);
    const seconds = Math.floor((time % 60000) / 1000);
    const milliseconds = (time % 1000).toString().slice(0, 2); // Display only the first two digits of milliseconds
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds}`;
  }
  ngOnInit() {
    this.initialize();
    this.startTimer();
    this.episodesForm = this.formBuilder.group({
      episodes: [''], // Initialize the episodes form control
    });
    this.episodesForm.get('episodes')?.valueChanges.pipe(
      distinctUntilChanged()
    ).subscribe((value) => {
      if (value !== null && value !== '') {
        this.episodes = value
      }
    });
  }


  initialize() {
    this.updateGameBoard(); // Call this once during initialization
    const gridSize = Math.sqrt(this.grid.length);
    for (let index = 0; index < this.grid.length; index++) {
      const row = Math.floor(index / gridSize);
      const col = index % gridSize;
      this.positionDictionary[`(${row},${col})`] = index;
    }
  }
  Play = () => {
    this.letsPlay = true
    this.completed = false

  }

  onCellClick(value: number, rowIndex: number, colIndex: number) {
    const position = this.positionDictionary[`(${rowIndex},${colIndex})`];

    if (!this.gameOver) {
      this.gameService.userMove(position).subscribe({
        next: () => {
          this.updateGameBoard();
        },
        error: (error) => {
          console.error('Error during user move:', error);
        }
      });
    }
    setTimeout(() => {
      if (!this.gameOver) {
        this.gameService.agentMove().subscribe({
          next: () => {
            this.updateGameBoard();
          },
          error: (error) => {
            console.error('Error during agent move:', error);
          }
        });
      }
    }, 300);

  }

  updateGameBoard() {
    this.gameService.getGameBoard().subscribe({
      next: (response: any) => {
        this.gameStatus = response.game_status;
        // Now check the game status and handle accordingly
        if (this.gameStatus === 'X Wins' || this.gameStatus === 'O Wins' || this.gameStatus === 'Draw') {
          this.gameInProgress = false;
          this.winner = this.gameStatus.toString();
          this.showOverlay = true;
          this.gameOver = true;
        } else {
          this.winner = '';
          this.showOverlay = false;
          this.gameOver = false;
        }
        this.gameBoard = response.board_state;
      },
      error: (error) => {
        console.error('Error fetching game board:', error);
      }
    });
  }

  downloadModel() {
    this.gameService.downloadModel().subscribe({
      next: (data: Blob) => {
        const blob = new Blob([data], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'trained_model.keras';
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Error downloading model:', error);
        // Handle error in UI
      }
    });
  }

  resetGame() {
    this.completed = false
    this.gameService.resetGame().subscribe(() => {
      this.updateGameBoard();
    });
  }

  trainAgent() {
    this.startTimer();
    this.displayTimer = true;
    this.loading = true;
    this.completed = false;
    this.resetGame();
    this.isButtonDisabled = true
    this.letsPlay = false
    this.gameService.trainAgent(this.episodes).subscribe({
      next: (status: any) => {
        this.trainingStaus = status;
        if (this.trainingStaus === 'complete') {
          this.completed = true;
          this.loading = false;
          this.isButtonDisabled = false
          this.stopTimer();
        }
        else if (this.trainingStaus === 'failed') {
          this.loading = false;
          this.completed = false
          this.stopTimer()
        }
      },
      error: (error: any) => {
        console.error('Error during training:', error);
      }
    });
  }

}
