# Champai

Champai jest kompilatorem prostego języka imperatywnego `glang` do kodu maszyny rejestrowej `GVM` powstałym na potrzeby kursu *Języki Formalne i Techniki Translacji* realizowanego w ramach studiów informatyki na *Wydziale Podstawowych Problemów Techniki* Politechniki Wrocławskiej.

### O kompilatorze

Champai został napisany w języku `Python` w oparciu o `SLY` - nowoczesną implementację narzędzi `lex` i `yacc` powszechnie wykorzystywanych do tworzenia parserów i kompilatorów. Tworzony z myślą o rozszerzalności i prostocie utrzymania, Champai charakteryzuje nieskomplikowana budowa i dobrze udokumentowany kod źródłowy.

## Wymagania systemowe

W celu uruchomienia kompilatora koniecznie jest zainstalowanie w systemie `Pythona` w wersji `3.6` lub nowszej oraz biblioteki `SLY`. W tym celu można skorzystać z przygotowanego skryptu `install.sh` lub ręcznie wywołać następujące polecenia: 

```sh
$ sudo apt update
$ sudo apt install python3 -y
$ sudo apt install python3-pip -y
$ pip3 install sly==0.3.0
```

## Kompilowanie przy użyciu Champai

Aby skompilować kod źródłowy programu napisanego w prostym języku imperatywnym `glang` do kodu maszynyy rejestrowej `GVM` przy użyciu kompilatora Champai należy w katalogu zawierającym plik `champai.py` użyć polecenia:

```sh
$ python3 champai.py [input_file] --out [output_file]
```

gdzie `input_file` oznacza nazwę lub ścieżkę do pliku źródłowego, a `output_file` - nazwę lub ścieżkę do pliku wynikowego.

Szczegółowe informacje dostępne są po wykonaniu komendy:
```sh
$ python3 champai.py -h
```

## Geneza nazwy
Nazwa Champai bierze się najprawdopodniej z języka fińskiego i powiązana jest z popularnym wśród tamtejszych górali zwrotem `jano, jano, jano!`[^1]. 

[^1]: Na podstawie wypowiedzi znawcy kultur ugrofińskich, dr *in spe* Macieja Kabały.
