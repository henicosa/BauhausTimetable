# Bauhaus Timetable - Bison - eInk Connector for information displays

## Introduction

Bauhaus Timetable connects the Bison course catalogue of the Bauhaus-Universität Weimar with eInk displays in the university buildings that show the next events happening in the rooms.

## Features

- [X] **Bison Connection**: Use a crawler to ectract all important information from the Bison website

### Requirements

- Docker

### Installation

1. Clone the repository: `git clone https://github.com/henicosa/BauhausTimetable.git`
2. Install and run docker container: `./install.sh`

### Usage

To customize and display the timetable, you can configure various parameters through the URL. Here's an example URL with parameters:

```plaintext
http://127.0.0.1:8000/raum?room_ids=2882,2883,2881,2884&building_name=Marienstra%C3%9Fe%2013&display_type=eink&current_time=2024-04-10
```

#### Available Parameters

- **room_ids**: Comma-separated list of room IDs. Defaults to "2882,2883,2881,2884".

- **building_name**: Name of the building. Defaults to "Unbenanntes Gebäude". Make sure to URL encode special characters.

- **display_type**: Type of display. Defaults to "online". Other Options are `eink` or `dark_eink`.

- **current_time**: Date to display the timetable. Defaults to the current date in the "YYYY-MM-DD" format.


## Contribution Guidelines

I welcome contributions from the community to improve and enhance Bauhaus Watch. If you would like to contribute, please follow these guidelines:

1. Fork the repository and create your branch: `git checkout -b my-feature`
2. Make changes and commit them: `git commit -m "Add feature"`
3. Push to your branch: `git push origin my-feature`
4. Open a pull request with a detailed description of the changes.

## License

Bauhaus Timetable is open-source software licensed under the [MIT License](LICENSE).

## Feedback and Support

If you encounter any issues, have suggestions, or need support, please open an issue on the repository. I appreciate your feedback and am committed to making Bauhaus Timetable better with your help!






