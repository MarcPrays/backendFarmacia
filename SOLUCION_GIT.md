# Solución para el Error 403 de Git

## Problema
Estás intentando hacer push a un repositorio que pertenece a `MarcPrays` pero estás autenticado como `ramirezandres7723-lgtm` y no tienes permisos.

## Soluciones

### Opción 1: Si el repositorio es TUYO (MarcPrays es tu cuenta)
Necesitas autenticarte correctamente:

1. **Actualizar credenciales de Git:**
   ```bash
   git config --global credential.helper manager-core
   ```

2. **Eliminar credenciales guardadas:**
   - En Windows: Panel de Control > Credenciales de Windows > Buscar "github.com" y eliminarlas
   - O ejecuta: `git credential-manager-core erase`

3. **Hacer push de nuevo** - Te pedirá autenticarte con el usuario correcto

### Opción 2: Si NO es tu repositorio
Tienes dos opciones:

**A) Hacer un Fork del repositorio:**
1. Ve a https://github.com/MarcPrays/backendFarmacia
2. Haz clic en "Fork"
3. Cambia el remoto a tu fork:
   ```bash
   git remote set-url origin https://github.com/TU_USUARIO/backendFarmacia.git
   git push origin luis
   ```

**B) Crear tu propio repositorio:**
1. Crea un nuevo repositorio en GitHub con tu cuenta
2. Cambia el remoto:
   ```bash
   git remote set-url origin https://github.com/TU_USUARIO/nombre-repositorio.git
   git push -u origin luis
   ```

### Opción 3: Usar SSH (Recomendado)
Si tienes claves SSH configuradas:

1. **Cambiar a SSH:**
   ```bash
   git remote set-url origin git@github.com:MarcPrays/backendFarmacia.git
   ```

2. **O si es tu repositorio:**
   ```bash
   git remote set-url origin git@github.com:TU_USUARIO/backendFarmacia.git
   ```

### Opción 4: Usar Personal Access Token
1. Ve a GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Genera un nuevo token con permisos `repo`
3. Usa el token como contraseña cuando Git te lo pida

## Verificar configuración actual
```bash
git remote -v
git config user.name
git config user.email
```

