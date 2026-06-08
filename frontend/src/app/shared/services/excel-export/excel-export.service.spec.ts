import { TestBed } from '@angular/core/testing';
import { ExcelExportService } from './excel-export.service';

describe('ExcelExportService', () => {
  let service: ExcelExportService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ExcelExportService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should generate a blob from data', async () => {
    const data = [
      { Name: 'Item 1', Price: 100 },
      { Name: 'Item 2', Price: 200 },
    ];

    const blob = await service.exportToExcel(data, 'TestSheet');
    expect(blob).toBeInstanceOf(Blob);
    expect(blob.type).toBe(
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    );
    expect(blob.size).toBeGreaterThan(0);
  });

  it('should handle empty data', async () => {
    const blob = await service.exportToExcel([], 'EmptySheet');
    expect(blob).toBeInstanceOf(Blob);
  });

  it('should trigger download with correct filename', async () => {
    const data = [{ Name: 'Item 1' }];
    const link = spyOn(document, 'createElement').and.callThrough();

    await service.downloadExcel(data, 'TestSheet', 'test-file.xlsx');

    expect(link).toHaveBeenCalledWith('a');
  });
});
