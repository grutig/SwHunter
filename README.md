# swhunter

**swhunter** is an open-source application designed for Shortwave Listening (SWL) and Broadcast Listening (BCL). It allows users to manage shortwave broadcast station schedules (based on the EiBi database) and control compatible radio receivers using [Hamlib](https://github.com/Hamlib/Hamlib), manage CRUD operations on database, search the database and lookup it based on receiver frequency, date, time and schedules.

> ⚠️ **Alpha Stage**: swhunter is currently in **alpha** development. While it is already **usable**, features may be incomplete or subject to change.

## Features

- Integration with the [EiBi shortwave broadcast database](https://www.eibispace.de/)
- Real-time control of radios via [Hamlib](https://github.com/Hamlib/Hamlib)
- Multi-receiver configuration support
- Filtering and searching broadcast schedules by frequency, time, language, and more
- Logging and session tracking for your listening activities (planned)

## Dependencies

- [Hamlib](https://github.com/Hamlib/Hamlib) (runtime and development libraries required)
- Qt5
- Python 3.11 or higher

# How to use

launch the application, config the rig(s), activate one of the rig. Click on the frequency to lookup the database for compatible transmissione, or use lookup menu call. 

# Disclaimer

Application is provided on "as is" terms with no warranty (see license for more information). Do not file Github issues with generic support requests.
