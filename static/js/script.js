/* static/js/script.js */
$(document).ready(function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Record page entry time
    const pageEntryTime = new Date().getTime();
    
    // Function to record page navigation
    function recordNavigation(destination) {
        const exitTime = new Date().getTime();
        const timeSpent = (exitTime - pageEntryTime) / 1000; // in seconds
        
        // Record data about the visit
        $.ajax({
            type: 'POST',
            url: '/save_user_data',
            data: {
                page_exit_time: exitTime,
                time_spent: timeSpent,
                destination: destination
            },
            success: function(response) {
                console.log('Navigation data recorded.');
            },
            error: function(error) {
                console.log('Error recording navigation data:', error);
            }
        });
    }
    
    // Track navigation button clicks
    $('a.btn').click(function() {
        const destination = $(this).attr('href');
        recordNavigation(destination);
    });
    
    // Track navigation through navbar
    $('.navbar-nav a').click(function() {
        const destination = $(this).attr('href');
        recordNavigation(destination);
    });
    
    // Handle quiz form submissions
    $('#quiz-form').submit(function() {
        const exitTime = new Date().getTime();
        const timeSpent = (exitTime - pageEntryTime) / 1000; // in seconds
        
        // Add hidden field with time data
        $('<input>').attr({
            type: 'hidden',
            name: 'time_spent',
            value: timeSpent
        }).appendTo('#quiz-form');
    });
    
    // Show/hide hint on quiz pages
    $('#hint-btn').click(function() {
        $('#hint-box').removeClass('d-none');
        
        // Record that user viewed hint
        $.ajax({
            type: 'POST',
            url: '/save_user_data',
            data: {
                viewed_hint: true
            }
        });
    });
    
    // Region flavor profile visualization enhancements
    $('.flavor-profile .progress').each(function() {
        const value = $(this).find('.progress-bar').attr('aria-valuenow');
        $(this).find('.progress-bar').css('width', (value * 20) + '%');
    });
    
    // Animate elements when they come into view
    function animateOnScroll() {
        $('.card').each(function() {
            const position = $(this).offset().top;
            const scroll = $(window).scrollTop();
            const windowHeight = $(window).height();
            
            if (scroll + windowHeight > position + 100) {
                $(this).addClass('animate__animated animate__fadeInUp');
            }
        });
    }
    
    // Initial check for elements in view
    animateOnScroll();
    
    // Check again on scroll
    $(window).scroll(function() {
        animateOnScroll();
    });
});