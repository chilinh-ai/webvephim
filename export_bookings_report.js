const fs = require('fs');
const XLSX = require('xlsx');

// Đọc dữ liệu JSON
const data = JSON.parse(fs.readFileSync('webvephim-main/webdatvexemphim-6f5a7-default-rtdb-export.json', 'utf8'));
const bookings = data.bookings;

const reportRows = [];

for (const cinema in bookings) {
  for (const date in bookings[cinema]) {
    let totalRevenueDay = 0;
    let showtimeCount = 0;
    for (const showtime in bookings[cinema][date]) {
      showtimeCount++;
      let bookedSeats = [];
      let showtimeRevenue = 0;
      for (const bookingId in bookings[cinema][date][showtime]) {
        const booking = bookings[cinema][date][showtime][bookingId];
        if (Array.isArray(booking.seats)) {
          bookedSeats = bookedSeats.concat(booking.seats);
        }
        if (booking.totalAmount) {
          showtimeRevenue += booking.totalAmount;
        }
      }
      totalRevenueDay += showtimeRevenue;
      reportRows.push({
        'Rạp': cinema,
        'Ngày': date,
        'Suất chiếu': showtime,
        'Ghế đã đặt': bookedSeats.join(', '),
        'Số ghế đã đặt': bookedSeats.length,
        'Doanh thu suất': showtimeRevenue
      });
    }
    // Thêm tổng kết theo ngày (nếu muốn)
    reportRows.push({
      'Rạp': cinema,
      'Ngày': date,
      'Suất chiếu': 'TỔNG NGÀY',
      'Ghế đã đặt': '',
      'Số ghế đã đặt': '',
      'Doanh thu suất': totalRevenueDay
    });
  }
}

// Tạo workbook và sheet
const wb = XLSX.utils.book_new();
const ws = XLSX.utils.json_to_sheet(reportRows);

// Định dạng cột doanh thu
const range = XLSX.utils.decode_range(ws['!ref']);
for (let R = 1; R <= range.e.r; ++R) {
  const cell = ws[`F${R+1}`];
  if (cell && typeof cell.v === 'number') {
    cell.z = '#,##0 "VNĐ"';
  }
}

XLSX.utils.book_append_sheet(wb, ws, 'Bookings Report');

// Xuất file Excel
XLSX.writeFile(wb, 'Bookings_Report.xlsx');

console.log('Đã xuất file Bookings_Report.xlsx thành công!');