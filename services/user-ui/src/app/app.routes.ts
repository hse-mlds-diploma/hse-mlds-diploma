import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'reviews', pathMatch: 'full' },
  { path: 'reviews', loadComponent: () => import('./reviews/reviews-list.component').then(m => m.ReviewsListComponent) },
  { path: 'reviews/new', loadComponent: () => import('./reviews/review-create.component').then(m => m.ReviewCreateComponent) },
];
