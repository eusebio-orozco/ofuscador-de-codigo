import ast, sys, random, os

def show_banner():
    banner = r"""
,---,---,---,---,---,---,---,---,---,---,---,---,---,-------,
|1/2| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 | + | ' | <-    |
|---'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-----|
| ->| | Q | W | E | R | T | Y | U | I | O | P | ] | ^ |     |
|-----',--',--',--',--',--',--',--',--',--',--',--',--'|    |
| Caps | A | S | D | F | G | H | J | K | L | \ | [ | * |    |
|----,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'-,-'---'----|
|    | < | Z | X | C | V | B | N | M | , | . | - |          |
|----'-,-',--'--,'---'---'---'---'---'---'-,-'---',--,------|
| ctrl |  | alt |                          |altgr |  | ctrl |
'------'  '-----'--------------------------'------'  '------'

[+] Ofuscador de codigo [+]
    """
    print(banner)


def get_libraries(file):
    with open(file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    return sorted({n.module if isinstance(n, ast.ImportFrom) else a.name for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)) for a in getattr(n, 'names', [])})

def extract_code(file):
    with open(file, "r", encoding="utf-8") as f:
        return ''.join(line for line in f if not line.strip().startswith("import"))

def generate_prime():
    while True:
        n = random.randint(1000, 1000000)
        if all(n % i for i in range(2, int(n**0.5) + 1)):
            return n

def random_str(length=30):
    chars = [chr(random.randint(65, 90)) for _ in range(length // 3)]
    chars += [chr(random.randint(97, 122)) for _ in range(length - len(chars))]
    random.shuffle(chars)
    return ''.join(chars)

def save_file(name, content, imports):
    with open(name, "w", encoding="utf-8") as f:
        f.writelines(f"import {lib}\n" for lib in imports)
        f.write("import random\n\n" + content)

def mod_exp(b, e, m):
    r = 1
    while e:
        if e & 1: r = (r * b) % m
        b = (b * b) % m
        e >>= 1
    return r

def mod_inv(a, m):
    r0, r1, s0, s1 = a, m, 1, 0
    while r1:
        q = r0 // r1
        r0, r1, s0, s1 = r1, r0 - q * r1, s1, s0 - q * s1
    return s0 % m

def encrypt_v1(code):
    prime, salt = generate_prime(), random.randint(1, 300)
    encrypted = [(prime * ord(c) + salt) % 256 for c in code]
    func = random_str()
    return f"""def {func}(p, c, s):
    t = {{(p*x + s)%256:x for x in range(256)}}
    return bytes([t[n] for n in [int(c[i:i+2],16) for i in range(0,len(c),2)]])

if __name__ == "__main__":
    p, s, c = {prime}, {salt}, "{''.join(hex(x)[2:].zfill(2) for x in encrypted)}"
    exec({func}(p, c, s).decode())"""

def encrypt_v2(code):
    salt, key = random.randint(50, 500), random.randint(10, 250)
    shuffle = list(range(256)); random.shuffle(shuffle)
    reverse = {v: k for k, v in enumerate(shuffle)}
    encrypted = [(shuffle[(b ^ key) % 256] + salt) % 256 for b in code.encode()]
    func = random_str()
    return f"""def {func}(c,k,s,r):
    return bytearray(r[(b - s)%256]^k for b in [int(c[i:i+2],16) for i in range(0,len(c),2)]).decode()

if __name__ == "__main__":
    c = "{''.join(hex(x)[2:].zfill(2) for x in encrypted)}"
    exec({func}(c, {key}, {salt}, {reverse}))"""

def encrypt_v3(code):
    p1, p2 = generate_prime(), generate_prime()
    n, e, phi = p1 * p2, 65537, (p1 - 1)*(p2 - 1)
    d = mod_inv(e, phi)
    encrypted = ','.join(str(mod_exp(ord(c), e, n)) for c in code)
    func = random_str()
    return f"""def {func}(e,d,n): return ''.join(chr(pow(int(x),d,n)) for x in e.split(','))

if __name__ == "__main__":
    e = "{encrypted}"; exec({func}(e,{d},{n}))"""

def encrypt_v4(code):
    key = [random.randint(1, 255) for _ in range(16)]
    enc = [ord(c) ^ key[i % 16] for i, c in enumerate(code)]
    func = random_str()
    return f"""def {func}(e,k): return ''.join(chr(e[i]^k[i%len(k)]) for i in range(len(e)))

if __name__ == "__main__":
    exec({func}({enc}, {key}))"""

ENCRYPTION_METHODS = {
    1: encrypt_v1,
    2: encrypt_v2,
    3: encrypt_v3,
    4: encrypt_v4
}

def choose_encryption_method():
    print("Programado por Eusebio de Jesus Gutierrez Orozco\n")
    print("Seleccione método de cifrado:\n")
    print("1. Cifrado con fórmula de número primo (método 1)")
    print("2. XOR + mezcla + salt aleatorio (método 2)")
    print("3. RSA simplificado (método 3)")
    print("4. XOR con clave rotatoria (método 4)")
    print("5. Ejecutar múltiples iteraciones aleatorias")
    
    while True:
        try:
            choice = int(input("\nOpción: "))
            if 1 <= choice <= 5:
                return choice
            else:
                print("Elige un número entre 1 y 5.")
        except ValueError:
            print("Entrada inválida.")

def encrypt(code, method_choice):
    if method_choice == 5:
        rounds = int(input("¿Cuántas iteraciones aleatorias quieres? (ej: 6): "))
        for _ in range(rounds):
            code = random.choice(list(ENCRYPTION_METHODS.values()))(code)
    else:
        code = ENCRYPTION_METHODS[method_choice](code)
    return code

if __name__ == "__main__":
    show_banner()

    if len(sys.argv) < 2:
        print("Uso: python script.py archivo.py")
        sys.exit(1)

    path = sys.argv[1]
    imports = get_libraries(path)
    original_code = extract_code(path)

    method = choose_encryption_method()
    encrypted_code = encrypt(original_code, method)

    #  Preguntar al usuario dónde guardar el archivo
    print("\n¿Dónde deseas guardar el archivo cifrado?")
    print("Puedes escribir solo un nombre (se guardará en la misma carpeta), o una ruta completa.")
    user_output_path = input("Ruta de salida (ej. salida.py o C:/Users/Eusebio/Documentos/salida.py): ").strip()

    if not user_output_path:
        user_output_path = os.path.basename(path)  # por defecto usa el nombre original

    save_file(user_output_path, encrypted_code, imports)
    print(f"\n Código cifrado guardado en: {user_output_path}")
