$(document).ready(function() {
    var table = $('#user-table').DataTable({
        // Your existing DataTables configuration
        "columns": [
            // Your existing columns
            { "data": "first_name" },
            { "data": "last_name" },
            { "data": "date_joined" },
            { "data": "email" },
            { "data": "sentiment_score" },
            { "data": "last_logged_in" },
            {
                "data": null,
                "defaultContent": '<button class="btn btn-info btn-sm details-btn">Details</button>',
                "orderable": false
            }
        ]
    });

    // Handle click event for the Details button
    $('#user-table tbody').on('click', 'button.details-btn', function() {
        var data = table.row($(this).parents('tr')).data();
        showUserDetails(data);
    });
});

function showUserDetails(userData) {
    // For now, using static content
    var detailsHTML = `
        <div>
            <h4>${userData.first_name || ''} ${userData.last_name || ''}</h4>
            <p><strong>Email:</strong> ${userData.email}</p>
            <p><strong>Joined:</strong> ${userData.date_joined}</p>
            <p><strong>Last Login:</strong> ${userData.last_logged_in || 'Never'}</p>
            <p><strong>Sentiment Score:</strong> ${userData.sentiment_score || 'N/A'}</p>
            <p><strong>Account Status:</strong> Active</p>
            <p><strong>User Type:</strong> Standard</p>
            <p><strong>Profile Completion:</strong> 75%</p>
        </div>
    `;

    // Show the modal with the details
    $('#userDetailsModal .modal-body').html(detailsHTML);
    $('#userDetailsModal').modal('show');
}