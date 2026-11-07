fetch('/trend_chart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
})
.then(response => response.json())
.then(data => {
    // 1. Update the Stat Cards
    document.getElementById('stat-total-bookings').innerText = data.stats.total_bookings;
    document.getElementById('stat-upcoming-bookings').innerText = data.stats.upcoming_bookings;
    document.getElementById('stat-total-revenue').innerText = '$' + data.stats.total_revenue.toLocaleString();
    document.getElementById('stat-hotels-booked').innerText = data.stats.hotels_with_bookings;

    // 2. Chart 1: Bookings by Month (Area Line Chart)
    const bookingsMonthCtx = document.getElementById('bookingsByMonthChart').getContext('2d');
    new Chart(bookingsMonthCtx, {
        type: 'line',
        data: {
            labels: data.bookings_by_month.map(item => item.month),
            datasets: [{
                label: 'Bookings',
                data: data.bookings_by_month.map(item => item.count),
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // 3. Chart 2: Revenue by Month (Bar Chart)
    const revenueMonthCtx = document.getElementById('revenueByMonthChart').getContext('2d');
    new Chart(revenueMonthCtx, {
        type: 'bar',
        data: {
            labels: data.revenue_by_month.map(item => item.month),
            datasets: [{
                label: 'Revenue ($)',
                data: data.revenue_by_month.map(item => item.revenue),
                backgroundColor: '#20c997'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // 4. Chart 3: Booking Type Mix (Doughnut Chart)
    const bookingTypeCtx = document.getElementById('bookingTypeMixChart').getContext('2d');
    new Chart(bookingTypeCtx, {
        type: 'doughnut',
        data: {
            labels: ['Hotel', 'Package'],
            datasets: [{
                data: [data.booking_type_mix["Hotel"], data.booking_type_mix["Package"]],
                backgroundColor: ['#0d6efd', '#ffc107'],
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // 5. Chart 4: Holiday Type Mix (Pie Chart)
    const holidayTypeCtx = document.getElementById('holidayTypeMixChart').getContext('2d');
    new Chart(holidayTypeCtx, {
        type: 'pie',
        data: {
            labels: ['Family', 'Food', 'Nature'],
            datasets: [{
                data: [data.holiday_type_mix["Family"], data.holiday_type_mix["Food"], data.holiday_type_mix["Nature"]],
                backgroundColor: ['#198754', '#fd7e14', '#6f42c1'],
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // 6. Chart 5: Top Hotels by Bookings (Horizontal Bar Chart)
    const topHotelsCtx = document.getElementById('topHotelsChart').getContext('2d');
    new Chart(topHotelsCtx, {
        type: 'bar',
        data: {
            labels: data.top_hotels.map(item => item.hotel),
            datasets: [{
                label: 'Bookings',
                data: data.top_hotels.map(item => item.count),
                backgroundColor: '#6f42c1'
            }]
        },
        options: { 
            indexAxis: 'y',
            responsive: true, 
            maintainAspectRatio: false 
        }
    });

    // 7. Chart 6: Bookings by Neighborhood (Bar Chart)
    const neighborhoodCtx = document.getElementById('neighborhoodChart').getContext('2d');
    new Chart(neighborhoodCtx, {
        type: 'bar',
        data: {
            labels: data.bookings_by_neighborhood.map(item => item.neighborhood),
            datasets: [{
                label: 'Bookings',
                data: data.bookings_by_neighborhood.map(item => item.count),
                backgroundColor: '#dc3545'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // 8. Chart 7: Most Suggested Activities in Itineraries (Horizontal Bar Chart)
    const activitiesCtx = document.getElementById('activitiesChart').getContext('2d');
    new Chart(activitiesCtx, {
        type: 'bar',
        data: {
            labels: data.most_suggested_activities.map(item => item.activity),
            datasets: [{
                label: 'Suggested Count',
                data: data.most_suggested_activities.map(item => item.count),
                backgroundColor: '#198754'
            }]
        },
        options: { 
            indexAxis: 'y',
            responsive: true, 
            maintainAspectRatio: false 
        }
    });

})
.catch(error => console.error("Error loading dashboard data:", error));