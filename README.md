# Numerical Expressions
This project contains a Python script that calculates and describes the change between two numerical values in various ways. The script takes two arguments: an initial value and a final value for comparison. The operations performed include percentage, percentage difference, ratio, and ratio difference.

Created by: Fer Aguirre

---

## Directory Structure

```
├── LICENSE
├── change_calculator.py
├── poetry.lock
├── pyproject.toml
└── README.md
```
---

## Getting Started

### Requirements

- Python 3.8 or higher
- [argparse](https://pypi.org/project/argparse/)
- [num2words](https://pypi.org/project/num2words/)
- [fraction](https://pypi.org/project/Fraction/)

### Installation 

To install the necessary dependencies, follow these steps:

1. Clone the repository to your local machine:

```
git clone https://github.com/fer-aguirre/numerical-expressions
```

2. Navigate to the project directory:

```
cd numerical-expressions
```

3. Install the dependencies using Poetry or pip accordingly:

```
poetry install
```

```
pip install -r requirements.txt
```

### Running the Script

To run the `change_calculator.py` script from the command line, use the following command:

```
python change_calculator.py <initial_value> <final_value>
```

Replace `<initial_value>` and `<final_value>` with the values you want to compare. For example:

```
python change_calculator.py 10 20
```

This will calculate and print the percentage, percentage difference, ratio, and ratio difference between 10 and 20.

## Contributing

All contributions are welcome. For major changes, please open an issue first to discuss what you would like to change. Pull requests are appreciated to help fix or add features.

## License

This project is released under [MIT License](/LICENSE).

## Acknowledgments

- [Math for Journalists Course](https://www.poynter.org/shop/self-directed-course/numeracy-primer-how-to-write-about-numbers/) by Poynter
- [Newsroom Math Crib Sheet](https://www.datovazurnalistika.cz/wp-content/uploads/2014/07/Newsroom-Math-Crib-Sheet-Steve-Doig.pdf) by Steve Doig

---

This repository was generated with [cookiecutter](https://github.com/cookiecutter/cookiecutter).