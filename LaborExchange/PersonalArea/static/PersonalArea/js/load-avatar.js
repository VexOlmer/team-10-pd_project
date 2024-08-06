
    function save ()  {
        let f = file1.files[0];
        if (f) {
            image1.src = URL.createObjectURL(f);
            localStorage.setItem('myImage', image1.src);
        }
    }

    image1.src = localStorage.getItem('myImage')
