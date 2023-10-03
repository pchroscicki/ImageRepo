# ImageRepository

Aim:    

ImageRepository is a web-based application, which creates thumbnails of the uploaded images by logged-in users.

Description:    

    1) User login process is govern by builtin Django function.

    2) Under `localhost:8000/api/schema/redoc` url you can find an application schema with endpoints input and output structure:
    	- GET:`/api/image/` endpoint output returns a list of all users' images with associated thumbnails and data. On the bottom of the template there is a form to upload a new image. The availability of the active urls to image files depends on user account tier. For more info see (3)
    	- POST:`/api/image/` endpoint saves an uploaded image and associated data in the database and creates 2 standard thumbnails: 400px and 200px in height. If the uploaded image is <400px or <200px height the thumbnails represents the original image. The image width is adjusted to preserve an image height/width proportion. The created image receives a reference and unique uuid number. The endpoint redirects to the endpoint with image details: GET:/api/image/<str: uuid> ) 
    	- GET:`/api/image/<str: uuid>/` endpoint display a detail information about the uploaded image and associated thumbnails. The availability of the active urls to image files depends on user account tier. For more info see (3).

    3) The user tiers determine the visibility of the active urls to the image. There are 3 predefined tiers:
    	- Basic - Gives the permit to receive only a link to the 200px thumbnail for a time specified in the form.
    	- Premium - Gives the permit to receive links to 200px and 400px thumbnail, as well as original image, but only for a time specified in the form.
    	- Enterprise - Gives the permit to receive links to 200px and 400px thumbnail, as well as original image as long as the user belongs to this tier.

    4) Application has user-friendly admin interface to display database with objects details and CRUD permits. Admin can create the custom thumbnail with specified minimal width or height of any previously uploaded image.  


Before first run:

    1) Create `.env` file with `DJANGO_SUPERUSER_PASSWORD=<your password>` in `ImageRepository` folder.

    2) Open terminal and run `docker compose up --build` command to build an docker containers and initialize the project.

    3) Open you web browser and go under `localhost:8000/api/image/` address.

    4) Login with username: `admin` and `<your password>` from `.env` folder.

Technology stack:

    • Python3   
    • DjangoRestFramework    
    • PosgreSQL         
    • Docker
