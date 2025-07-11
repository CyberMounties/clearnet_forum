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

    // Modified function to load post details dynamically
    function loadPostDetails() {
        if ($('#post-title').length) { // Check if on post detail page
            console.log('Loading post details for:', postType, postId); // Debug log
            $.get(`/api/post/${postType}/${postId}`, function(data) {
                console.log('API response:', data); // Debug log
                const post = data.post;
                const comments = data.comments;
                const user = data.user;

                // Update post title
                $('#post-title').text(post.title || 'Untitled');

                // Update post content
                let contentHtml = '';
                if (postType === 'announcements') {
                    contentHtml = post.content || '';
                } else {
                    contentHtml = `${post.description || ''}<br><strong>Price:</strong> ${post.price || 'N/A'}`;
                }
                contentHtml += `<br><br><strong>Posted by:</strong> <a href="/profile/${post.username}" class="text-light">${post.username}</a>`;
                contentHtml += `<br><strong>Date:</strong> ${post.date}`;
                $('#post-content').html(contentHtml);

                // Update category
                $('#post-category').text(post.category || 'N/A');

                // Update comments
                $('#comments-section').empty();
                if (comments && comments.length > 0) {
                    comments.forEach(function(comment) {
                        $('#comments-section').append(
                            `<div class="mb-3">
                                <p class="text-light"><strong>${comment.username}</strong> (${comment.date}): ${comment.content}</p>
                            </div>`
                        );
                    });
                } else {
                    $('#comments-section').html('<p class="text-light">No comments yet.</p>');
                }

                // Update back link
                $('#back-link').attr('href', `/category/${postType}/${post.category}`).text(`Back to ${post.category}`);
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.error('Failed to load post details:', textStatus, errorThrown); // Debug log
                if (jqXHR.status === 429) {
                    // Handle rate limit exceeded
                    const response = jqXHR.responseJSON;
                    const retryAfter = response ? response.retry_after : 'a short while';
                    $('#post-title').text('Rate Limit Exceeded');
                    $('#post-content').html(
                        `<p class="text-light">You've made too many requests.</p>` +
                        `<p class="text-light"><a href="/home" class="text-light">Go to Home</a></p>`
                    );
                    $('#comments-section').html('<p class="text-light">Comments unavailable due to rate limit.</p>');
                } else {
                    // Handle other errors (e.g., 404, 401)
                    $('#post-title').text('Error');
                    $('#post-content').html('<p class="text-light">Failed to load post. Please try again later.</p>');
                    $('#comments-section').html('<p class="text-light">Failed to load comments.</p>');
                }
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

    // Load data on post detail page
    loadPostDetails();

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