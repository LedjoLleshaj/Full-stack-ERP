import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  description: string;
}

@Component({
  selector: 'app-products-view',
  templateUrl: './products-view.component.html',
  styleUrls: ['./products-view.component.scss']
})
export class ProductsViewComponent implements OnInit {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  displayedColumns: string[] = ['id', 'name', 'category', 'price', 'description'];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchProducts();
  }

  fetchProducts() {
                            //  make the link to be 0.0.0.0 for Ledjo
    this.http.get<Product[]>('http://127.0.0.1:8080/selita/products').subscribe(data => {
      this.products = data;
      this.filteredProducts = data; // Initialize filteredProducts
    });
  }

  onSearchNameChange(event: any) {
    const searchTerm = event.target.value.toLowerCase();
    this.filteredProducts = this.products.filter(product => 
      product.name.toLowerCase().includes(searchTerm)
    );
  }
}
