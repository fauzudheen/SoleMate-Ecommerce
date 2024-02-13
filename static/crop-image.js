$(document).ready(function () {
    const alertBox = $('#alert-box');
    const imageBox = $('#image-box');
    const imageForm = $('#image-form');
    const confirmBtn = $('#confirm-btn');
    const input = $('#id_thumbnail');

    input.on('change', function () {
        alertBox.html('');
        confirmBtn.removeClass('not-visible');
        const imgData = input[0].files[0];
        const url = URL.createObjectURL(imgData);

        imageBox.html(`<img src="${url}" id="image" width="700px">`);
        const $image = $('#image');

        $image.cropper({
            aspectRatio: 16 / 9,
            crop: function (event) {
                console.log(event.detail);
            }
        });

        confirmBtn.on('click', function () {
            const cropper = $image.data('cropper');
            cropper.getCroppedCanvas().toBlob(function (blob) {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
                formData.append('thumbnail', blob, 'cropped-image.jpg');

                $.ajax({
                    type: 'POST',
                    url: imageForm.attr('action'),
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function (response) {
                        console.log('Success:', response);
                        alertBox.html('<div class="alert alert-success" role="alert">Successfully saved and cropped the selected image</div>');
                    },
                    error: function (error) {
                        console.error('Error:', error);
                        alertBox.html('<div class="alert alert-danger" role="alert">Oops... Something went wrong</div>');
                    }
                });
            });
        });
    });
});
