// static/js/main.js
$(document).ready(function() {
    // Function to load shoutbox
    function loadShoutbox() {
        $.get('/api/shoutbox', function(data) {
            $('#shoutbox').empty();
            data.forEach(function(item) {
                $('#shoutbox').append(
                    `<p><strong>${item.username}</strong> (${item.timestamp}): ${item.message}</p>`
                );
            });
        });
    }

    // Function to load category counts
    function loadCategoryCounts() {
        $.get('/api/category_counts', function(data) {
            $('#announcements-count').text(data.announcements.Announcements);
            $('#general-count').text(data.announcements.General);
            $('#mm-service-count').text(data.announcements['MM Service']);
            $('#buyers-count').text(data.marketplace.Buyers);
            $('#sellers-count').text(data.marketplace.Sellers);
            $('#sell-services-count').text(data.services.Sell);
            $('#buy-services-count').text(data.services.Buy);
        });
    }

    // Function to load category posts
    function loadCategoryPosts() {
        // Extract post_type and category from URL (e.g., /category/announcements/Announcements)
        const path = window.location.pathname.split('/');
        const post_type = path[2];
        const category = path[3];
        if (post_type && category) {
            $.get(`/api/posts/${post_type}/${category}`, function(data) {
                $('#category-posts-table').empty();
                data.forEach(function(item) {
                    $('#category-posts-table').append(
                        `<tr>
                            <td>${item.title}</td>
                            <td>${item.username}</td>
                            <td>${item.date}</td>
                            <td>${item.comments}</td>
                            <td><button class="btn btn-outline-secondary btn-sm view-post-btn" data-post-type="${post_type}" data-post-id="${item.id}">View</button></td>
                        </tr>`
                    );
                });
            });
        }
    }

    // Load data on home page
    if ($('#shoutbox').length) {
        loadShoutbox();
        loadCategoryCounts();
    }

    // Load data on category page
    if ($('#category-posts-table').length) {
        loadCategoryPosts();
    }

    // Handle shoutbox form submission (simulated)
    $('#shoutbox-form').submit(function(e) {
        e.preventDefault();
        let message = $('#shoutbox-message').val();
        if (message) {
            $('#shoutbox').prepend(
                `<p><strong>Guest</strong> (${new Date().toISOString()}): ${message}</p>`
            );
            $('#shoutbox-message').val('');
        }
    });

    // Handle search form submission (simulated)
    $('#search-form').submit(function(e) {
        e.preventDefault();
        let query = $('#search-query').val();
        let type = $('#filter-type').val();
        $.get('/api/' + (type || 'marketplace'), function(data) {
            $('#search-results').empty();
            data.filter(function(item) {
                return item.title.toLowerCase().includes(query.toLowerCase()) ||
                       (item.description || item.content || '').toLowerCase().includes(query.toLowerCase());
            }).forEach(function(item) {
                $('#search-results').append(
                    `<tr>
                        <td>${item.category}</td>
                        <td>${item.title}</td>
                        <td>${item.description || item.content || ''}</td>
                        <td>${item.username}</td>
                        <td>${item.price || ''}</td>
                        <td>${item.date}</td>
                    </tr>`
                );
            });
        });
    });

    // Handle view post button (placeholder)
    $(document).on('click', '.view-post-btn', function() {
        const postType = $(this).data('post-type');
        const postId = $(this).data('post-id');
        alert(`View post: ${postType} ID ${postId}`); // Placeholder for post detail view
    });
});
