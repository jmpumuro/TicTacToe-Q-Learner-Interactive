import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'toMatrix'
})
export class ToMatrixPipe implements PipeTransform {
  transform(array: number[]): number[][] {
    const matrix = [];

    for (let i = 0; i < array?.length; i += 3) {
      matrix.push(array.slice(i, i + 3));
    }

    return matrix;
  }
}
