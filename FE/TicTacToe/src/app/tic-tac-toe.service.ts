import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TicTacToeService {
  private baseUrl = 'http://127.0.0.1:8000/';

  constructor(private http: HttpClient) { }

  agentMove() {
    return this.http.get(`${this.baseUrl}agent-move/`);
  }

  userMove(position: number) {
    return this.http.post(`${this.baseUrl}user-move/`, { position });
  }

  trainAgent(episodes:number, epsilon:number, gamma:number) {
    return this.http.post(`${this.baseUrl}train-agent/`, {episodes,epsilon,gamma});
  }
  resetGame() {
    return this.http.post(`${this.baseUrl}reset-game/`, {});
  }

  getGameBoard() {
    return this.http.get(`${this.baseUrl}game-board/`);
  }

  downloadModel(): Observable<Blob> {
    const url = `${this.baseUrl}download-model/`; 
    return this.http.get(url, { responseType: 'blob' });
  }

}

