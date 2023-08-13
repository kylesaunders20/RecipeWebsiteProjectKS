$(document).ready(function(){
    $('.view-recipe').click(function(){
        const recipeName = $(this).data('name');
        const recipeImage = $(this).data('image');
        const recipeIngredients = $(this).data('ingredients');
        const recipePreparation = $(this).data('preparation');
        const recipeServing = $(this).data('serving');
        $('#recipeModalLabel').text(recipeName);
        $('#recipeImage').attr('src', recipeImage);
        $('#recipeIngredients').text(recipeIngredients);
        $('#recipePreparation').text(recipePreparation);
        $('#recipeServing').text(recipeServing);
        $('#recipeModal').modal('show');
    });
    $('#submitRating').click(function() {
        const recipeName = $('#recipeModalLabel').text();
        const selectedRating = $('input[name="rating"]:checked').val();
        if (!selectedRating) {
            alert("Please select a rating before submitting.");
            return;
        }
        $.post("/rate_recipe", {
            recipe_name: recipeName,
            rating: selectedRating
        }, function (data) {
            if (data.success) {
                $('.average-rating-div[data-name="' + recipeName + '"]').text("Average Rating: " + data.average_rating);
                location.reload();
            } else {
                alert(data.message || "An error occurred while submitting the rating.");
            }
        });
    });
});


