import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-reviews-list',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, RouterLink],
  templateUrl: './reviews-list.component.html',
  styleUrls: ['./reviews-list.component.scss']
})
export class ReviewsListComponent {
  reviews: any[] = [];
  loading = true;
  error: string | null = null;

  constructor(private http: HttpClient) {
    this.fetchReviews();
  }

  fetchReviews() {
    this.loading = true;
    this.http.get<any[]>('http://localhost:8000/api/v1/reviews')
      .subscribe({
        next: (data) => {
          this.reviews = data;
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Ошибка загрузки отзывов';
          this.loading = false;
        }
      });
  }
}
