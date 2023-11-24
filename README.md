# SnapShare-API

## About The Project

SnapShare is a robust photo-sharing application designed to facilitate the seamless exchange of images among users. At its core, it's built on the high-performance FastAPI framework and boasts a RESTful API backend brimming with features. This application is not just a project; it's a showcase of modern web application development expertise, ready to be a part of your portfolio.

### Features

- **Authentication:** Securely implemented via JWT tokens. It supports multiple user roles, including regular users, moderators, and administrators.
- **Image Operations:** Users can upload, delete, and update image descriptions. Images are accessible via unique links.
- **Tagging:** Add up to 5 unique tags per image, with reusable tags across the application.
- **Image Transformations:** Powered by Cloudinary for advanced operations. Transform images, generate viewable links, and create QR codes.
- **Commenting System:** Users can comment on each image, complete with timestamps. Admins have moderation capabilities.
- **User Profiles:** Users can view and edit their profiles, highlighting their activity and contributions.
- **Administration:** Extended controls for administrators, including user management and content moderation.

### Built With

- FastAPI
- PostgreSQL
- SQLAlchemy
- Cloudinary
- JWT for Authentication

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python Environment
- Poetry Package Manager

### Installation

1. Clone the repo:
   ```sh
   git clone https://github.com/your-repo/snapshare-api.git
   ```
2. Navigate to the project directory:
   ```sh
   cd snapshare-api
   ```
3. Initialize the project using Poetry:
   ```sh
   poetry install
   ```
4. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

## Usage

For a detailed guide on how to use SnapShare, please refer to the [documentation](https://snapshare-api.fly.dev/docs#/).

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement". Don't forget to give the project a star! Thanks again!

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Feel free to reach out to any of our team members:

- Dmytro Klymenko - [GitHub](https://github.com/leegosx) | [LinkedIn](https://www.linkedin.com/in/dmytro-klymenko-ab1356290/)
- Dmytro Filin - [GitHub](https://github.com/UkrainianEagleOwl) | [LinkedIn](https://www.linkedin.com/in/dmytro-filin-18716b198/)
- Illya Hryhoriev - [GitHub](https://github.com/Adentas)
- Dmytro Paukov - [GitHub](https://github.com/paukdv)