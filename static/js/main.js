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
            $('#announcements-count').text(data.announcements.Announcements || 0);
            $('#general-count').text(data.announcements.General || 0);
            $('#mm-service-count').text(data.announcements['MM Service'] || 0);
            $('#buyers-count').text(data.marketplace.Buyers || 0);
            $('#sellers-count').text(data.marketplace.Sellers || 0);
            $('#sell-services-count').text(data.services.Sell || 0);
            $('#buy-services-count').text(data.services.Buy || 0);
        }).fail(function() {
            console.error('Failed to load category counts');
        });
    }

    // Function to load category posts with pagination
    function loadCategoryPosts() {
        const path = window.location.pathname.split('/');
        const post_type = path[2];
        const category = path[3];
        const urlParams = new URLSearchParams(window.location.search);
        const page = urlParams.get('page') || 1;
        if (post_type && category) {
            $.get(`/api/posts/${post_type}/${category}?page=${page}`, function(data) {
                $('#category-posts-table').empty();
                data.posts.forEach(function(item) {
                    $('#category-posts-table').append(
                        `<tr>
                            <td>${item.title}</td>
                            <td><a href="/profile/${item.username}" class="text-light">${item.username}</a></td>
                            <td>${item.date}</td>
                            <td>${item.comments}</td>
                            <td><a href="/post/${post_type}/${item.id}" class="btn btn-outline-secondary btn-sm">View</a></td>
                        </tr>`
                    );
                });
                // Render pagination links
                const totalPages = data.total_pages;
                const currentPage = data.current_page;
                let paginationHtml = `Page ${currentPage} of ${totalPages}`;
                $('#pagination-links').html(paginationHtml);
                if (totalPages > 1) {
                    $('#next-page').attr('href', `/category/${post_type}/${category}?page=${currentPage + 1}`);
                    if (currentPage >= totalPages) {
                        $('#next-page').parent().addClass('disabled');
                    }
                } else {
                    $('#next-page').parent().addClass('disabled');
                }
            }).fail(function() {
                $('#category-posts-table').html('<tr><td colspan="5" class="text-light">You need to be logged in to see that.</td></tr>');
            });
        }
    }

    // Load data on home page
    if ($('#shoutbox').length) {
        loadShoutbox();
        loadCategoryCounts();
        // Poll shoutbox every 5 seconds
        setInterval(loadShoutbox, 5000);
    }

    // Load data on marketplace or services page
    if ($('#buyers-count').length || $('#sellers-count').length || $('#sell-services-count').length || $('#buy-services-count').length) {
        loadCategoryCounts();
        // Poll category counts every 60 seconds to reflect sellers_simulator.py updates
        setInterval(loadCategoryCounts, 60000);
    }

    // Load data on category page
    if ($('#category-posts-table').length) {
        loadCategoryPosts();
    }

    // Handle shoutbox form submission
    $('#shoutbox-form').submit(function(e) {
        e.preventDefault();
        let message = $('#shoutbox-message').val();
        if (message) {
            $('#shoutbox').prepend(
                `<p><strong>${currentUser || 'Guest'}</strong> (${new Date().toISOString()}): ${message}</p>`
            );
            $('#shoutbox-message').val('');
        }
    });

    // Handle search form submission
    $('#search-form').submit(function(e) {
        e.preventDefault();
        let query = $('#search-query').val();
        let type = $('#filter-type').val();
        $.get(`/api/search?query=${encodeURIComponent(query)}&type=${type}`, function(data) {
            $('#search-results').empty();
            data.forEach(function(item) {
                $('#search-results').append(
                    `<tr>
                        <td>${item.category}</td>
                        <td><a href="/post/${item.post_type}/${item.id}" class="text-light">${item.title}</a></td>
                        <td>${item.description || item.content || ''}</td>
                        <td><a href="/profile/${item.username}" class="text-light">${item.username}</a></td>
                        <td>${item.price || ''}</td>
                        <td>${item.date}</td>
                    </tr>`
                );
            });
        }).fail(function() {
            $('#search-results').html('<tr><td colspan="6" class="text-light">You need to be logged in to see that.</td></tr>');
        });
    });
});