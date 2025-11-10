import argparse

def main():
    # Utworzenie parsera
    parser = argparse.ArgumentParser(
        description='Opis programu',
        epilog='Dodatkowe informacje na końcu pomocy'
    )
    
    # Dodanie argumentów
    parser.add_argument('input', help='Plik wejściowy')
    parser.add_argument('-o', '--output', help='Plik wyjściowy')
    
    # Parsowanie argumentów
    args = parser.parse_args()
    
    # Użycie argumentów
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")

if __name__ == '__main__':
    main()