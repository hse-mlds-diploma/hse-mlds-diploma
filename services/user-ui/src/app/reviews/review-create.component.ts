import { Component, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-review-create',
  standalone: true,
  imports: [CommonModule, FormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatSelectModule, MatProgressSpinnerModule, MatIconModule, RouterLink],
  templateUrl: './review-create.component.html',
  styleUrls: ['./review-create.component.scss']
})
export class ReviewCreateComponent {
  review = {
    product_id: '',
    user_id: '',
    rating: 5,
    text: ''
  };
  loading = false;
  error: string | null = null;
  success = false;
  selectedFiles: File[] = [];
  photoIds: number[] = [];
  products = [
    { id: 1, name: 'Product 1' },
    { id: 2, name: 'Product 2' },
    { id: 3, name: 'Product 3' }
  ];
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  constructor(private http: HttpClient, private router: Router) {}

  onFilesSelected(event: any) {
    this.selectedFiles = Array.from(event.target.files);
  }

  async submit() {
    this.loading = true;
    this.error = null;
    this.photoIds = [];
    try {
      if (this.selectedFiles.length > 0) {
        for (const file of this.selectedFiles) {
          const formData = new FormData();
          formData.append('file', file);
          const res: any = await this.http.post('http://localhost:8000/api/v1/images/upload', formData).toPromise();
          if (res && res.photo_id) {
            this.photoIds.push(res.photo_id);
          }
        }
      }
      const reviewPayload = {
        ...this.review,
        rating: +this.review.rating,
        photo_ids: this.photoIds
      };
      await this.http.post('http://localhost:8000/api/v1/reviews', reviewPayload).toPromise();
      this.success = true;
      this.loading = false;
      setTimeout(() => this.router.navigate(['/reviews']), 1000);
    } catch (e) {
      this.error = 'Ошибка при отправке отзыва';
      this.loading = false;
    }
  }

  openFileDialog() {
    this.fileInput.nativeElement.click();
  }
}
