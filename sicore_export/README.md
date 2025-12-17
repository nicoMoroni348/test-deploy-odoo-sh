# SICORE Export - Módulo de Exportación AFIP

## Descripción General

El módulo **SICORE Export** permite generar archivos TXT según el formato oficial SICORE de AFIP (Argentina) para la declaración de:

- **Retenciones** (Impuesto a las Ganancias)
- **Percepciones** (Ingresos Brutos)
- **Combustibles** (compras de combustible)

### Características Principales

- ✅ Formatos AFIP actualizados (versión 8.0)
- ✅ Validación automática de CUIT con dígito verificador
- ✅ Mapeo automático de tipos de documento argentinos
- ✅ Catálogos SICORE precargados (impuestos, regímenes, tipos de documento)
- ✅ Logs de exportación con trazabilidad completa
- ✅ Soporte multiempresa
- ✅ Control de acceso por grupos (Usuario / Administrador)

---

## Instalación

### Requisitos Previos

- Odoo 17.0 Community
- Módulo de localización argentina (`l10n_ar`)
- Módulo de contabilidad (`account`)

### Pasos de Instalación

1. Copiar la carpeta `sicore_export` en el directorio de addons
2. Actualizar lista de aplicaciones en Odoo
3. Buscar "SICORE Export" e instalar
4. Los catálogos SICORE se cargarán automáticamente

---

## Configuración Inicial

### 1. Configurar Cuentas Contables

Las cuentas contables determinan qué tipo de registro SICORE genera cada apunte.

**Ruta:** `Contabilidad > Configuración > Plan de Cuentas`

| Campo | Descripción | Valores |
|-------|-------------|---------|
| **Exportación SICORE** | Define el tipo de exportación | `No exportar`, `Retenciones`, `Percepciones`, `Combustibles` |

#### Ejemplos de Configuración:

| Cuenta | Nombre | Exportación SICORE |
|--------|--------|-------------------|
| 2.1.3.01 | Retenciones Ganancias a Pagar | **Retenciones** |
| 2.1.3.02 | Percepciones IIBB a Pagar | **Percepciones** |
| 6.1.4.01 | Combustibles | **Combustibles** |
| 1.1.1.01 | Caja | No exportar |

---

### 2. Configurar Diarios Contables

Los diarios permiten filtrar qué asientos se exportan (excluir presupuestos, por ejemplo).

**Ruta:** `Contabilidad > Configuración > Diarios`

| Campo | Descripción | Valores |
|-------|-------------|---------|
| **Tipo Exportación SICORE** | Define si el diario exporta a SICORE | `Facturas Reales`, `Presupuestos`, `Ambos` |

#### Ejemplos de Configuración:

| Diario | Tipo | Exportación SICORE |
|--------|------|-------------------|
| Facturas de Compra | Compra | **Facturas Reales** |
| Facturas de Venta | Venta | **Facturas Reales** |
| Presupuestos | Varios | **Presupuestos** (excluido de exportación) |
| Pagos | Banco | **Facturas Reales** |

> **Nota:** Los diarios marcados como "Presupuestos" se excluyen automáticamente de las exportaciones de Retenciones y Percepciones.

---

### 3. Configurar Impuestos

**Esta es la configuración más importante.** Los códigos de impuesto y régimen SICORE se configuran en cada impuesto de retención/percepción.

**Ruta:** `Contabilidad > Configuración > Impuestos`

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Código Impuesto SICORE** | Código AFIP del impuesto | `[0217] Impuesto a las ganancias` |
| **Código Régimen SICORE** | Código AFIP del régimen | `[078] Enajenación de Bienes muebles` |

#### Códigos de Impuesto Disponibles:

| Código | Descripción |
|--------|-------------|
| 0217 | Impuesto a las Ganancias |
| 0767 | Ingresos Brutos (Percepciones) |

#### Códigos de Régimen Disponibles:

| Código | Descripción | Aplica a |
|--------|-------------|----------|
| 027 | Alquiler de bienes muebles e inmuebles | Retenciones |
| 035 | Regalías | Retenciones |
| 046 | Dividendos | Retenciones |
| 078 | Enajenación de Bienes muebles y bienes de cambio | Ambos |
| 094 | Locación de Obras o Servicios | Retenciones |
| 099 | Factura M | Ambos |
| 116 | Honorarios directores/Profesiones liberales | Retenciones |
| 160 | Rentas del trabajo bajo Relación de dependencia | Retenciones |
| 602 | Percepciones IIBB | Percepciones |
| 691 | Vales de almuerzo o canasta familiar | Retenciones |
| 775 | Retenciones a monotributistas | Retenciones |

#### Ejemplo de Configuración de Impuesto:

```
Nombre: Retención Ganancias 28%
Tipo: Retención
Cuenta de Impuesto: 2.1.3.01 - Retenciones Ganancias a Pagar
Código Impuesto SICORE: [0217] Impuesto a las ganancias
Código Régimen SICORE: [078] Enajenación de Bienes muebles
```

---

### 4. Configurar Contactos (Partners)

Los contactos necesitan tener configurado el tipo de identificación para el mapeo automático a SICORE.

**Ruta:** `Contactos > [Seleccionar contacto] > Pestaña Ventas y Compras`

| Campo | Descripción | Valores |
|-------|-------------|---------|
| **Tipo de Identificación** | Tipo de documento argentino | CUIT, CUIL, DNI, etc. |
| **Nro. Identificación** | Número de documento | Ej: 30-12345678-9 |
| **Régimen SICORE** | Régimen fiscal del contacto | `Régimen General`, `Régimen Simplificado` |

#### Mapeo Automático de Tipos de Documento:

| Tipo Argentino | Código SICORE |
|----------------|---------------|
| CUIT | 80 |
| CUIL | 86 |

> **Nota:** El tipo de documento SICORE se calcula automáticamente a partir del tipo de identificación argentino configurado.

---

## Uso del Módulo

### Acceso al Wizard de Exportación

**Ruta:** `Contabilidad > SICORE > Exportar SICORE`

### Pasos para Generar un Archivo TXT

1. Seleccionar **Tipo de Exportación**: Retenciones, Percepciones o Combustibles
2. Configurar el **rango de fechas** del período a exportar
3. (Opcional) Filtrar por **diarios** específicos
4. (Opcional) Filtrar por **régimen** del partner (General/Simplificado)
5. Verificar la **vista previa** con el resumen de registros
6. Hacer clic en **"Generar Exportación"**
7. El archivo TXT se descargará automáticamente

### Vista Previa

El wizard muestra un resumen con:
- Cantidad total de registros a exportar
- Detalle por partner (cantidad y montos)
- Período seleccionado

---

## Formatos de Archivo Generados

### Retenciones (197 caracteres por línea)

Archivo de posición fija con 21 campos:

| # | Campo | Longitud | Ejemplo |
|---|-------|----------|---------|
| 1 | Código Comprobante | 2 | `01` |
| 2 | Fecha Emisión Comprobante | 10 | `15/09/2025` |
| 3 | Número Comprobante | 16 | `0000000012345678` |
| 4 | Importe Comprobante | 16 | `0000000150000,00` |
| 5 | Código Impuesto | 3 | `217` |
| 6 | Código Régimen | 3 | `078` |
| 7 | Código Operación | 1 | `1` |
| 8 | Base Cálculo | 14 | `00000124000,00` |
| 9 | Fecha Emisión Retención | 10 | `15/09/2025` |
| 10 | Código Condición | 2 | `01` |
| 11 | Sujetos Suspendidos | 1 | `0` |
| 12 | Importe Retención | 14 | `00000034720,00` |
| 13 | Porcentaje Exclusión | 6 | `000000` |
| 14 | Fecha Vigencia | 10 | `15/09/2025` |
| 15 | Tipo Documento | 2 | `80` |
| 16 | Número Documento | 20 | `00000000030707753303` |
| 17 | Nro Certificado Original | 14 | `00000000000000` |
| 18 | Denominación Ordenante | 30 | `PROVEEDOR S.A.` |
| 19 | Acrecentamiento | 1 | `0` |
| 20 | CUIT País Retenido | 11 | `30707753303` |
| 21 | CUIT Ordenante | 11 | `30707753303` |

**Ejemplo de línea:**
```
0115/09/20250000000012345678000000015000000217078100000012400000015/09/20250100000000347200000000015/09/20258000000000030707753303000000000000              PROVEEDOR S.A.030707753303 30707753303
```

---

### Percepciones (144 caracteres por línea)

Archivo de posición fija con 17 campos:

| # | Campo | Longitud | Ejemplo |
|---|-------|----------|---------|
| 1 | Código Comprobante | 2 | `01` |
| 2 | Fecha Emisión Comprobante | 10 | `20/10/2025` |
| 3 | Número Comprobante | 16 | `0000000087654321` |
| 4 | Importe Comprobante | 16 | `0000000250000,00` |
| 5 | Código Impuesto | 3 | `767` |
| 6 | Código Régimen | 3 | `602` |
| 7 | Código Operación | 1 | `1` |
| 8 | Base Cálculo | 14 | `00000206611,57` |
| 9 | Fecha Emisión Percepción | 10 | `20/10/2025` |
| 10 | Código Condición | 2 | `01` |
| 11 | Sujetos Suspendidos | 1 | `0` |
| 12 | Importe Percepción | 14 | `00000005165,29` |
| 13 | Porcentaje Exclusión | 6 | `000000` |
| 14 | Fecha Emisión Boletín | 10 | `0000000000` |
| 15 | Tipo Documento | 2 | `80` |
| 16 | Número Documento | 20 | `00000000030543035064` |
| 17 | Nro Certificado Original | 14 | `00000000000000` |

**Ejemplo de línea:**
```
0120/10/2025000000008765432100000002500000076760210000002066115720/10/2025010000000051652900000000000000008000000000030543035064 00000000000000
```

---

### Combustibles (CSV separado por punto y coma)

Formato CSV con 11 campos:

| # | Campo | Ejemplo |
|---|-------|---------|
| 1 | Código Registro | `C` |
| 2 | Razón Social Proveedor | `BARALE S.A. - 306` |
| 3 | CUIT Proveedor | `30543035064` |
| 4 | Código Impuesto | `5` |
| 5 | Código Régimen | `001` |
| 6 | Número Comprobante | `2300041130` |
| 7 | Fecha Comprobante | `27092025` |
| 8 | Razón Social Cliente | `TOSTADERO MANICOP S.R.L.` |
| 9 | CUIT Cliente | `30707753303` |
| 10 | Código Constante | `3` |
| 11 | Importe | `44680,51` |

**Ejemplo de línea:**
```
C;BARALE S.A. - 306;30543035064;5;001;2300041130;27092025;TOSTADERO MANICOP S.R.L.;30707753303;3;44680,51
```

---

## Casos de Prueba

### Caso 1: Exportar Retenciones de Ganancias

**Configuración previa:**

1. **Cuenta contable:** 
   - Código: `2.1.3.01`
   - Nombre: `Retenciones Ganancias a Pagar`
   - Exportación SICORE: **Retenciones**

2. **Impuesto:**
   - Nombre: `Retención Ganancias 28%`
   - Tipo: Retención (negativo)
   - Cuenta: `2.1.3.01`
   - Código Impuesto SICORE: `[0217] Impuesto a las ganancias`
   - Código Régimen SICORE: `[078] Enajenación de Bienes muebles`

3. **Proveedor:**
   - Nombre: `Proveedor Test S.A.`
   - Tipo Identificación: `CUIT`
   - CUIT: `30-12345678-9`

**Pasos de prueba:**

1. Crear una factura de proveedor por $100.000
2. Aplicar el impuesto de retención 28% → Retención: $28.000
3. Publicar la factura
4. Ir a `Contabilidad > SICORE > Exportar SICORE`
5. Seleccionar "Retenciones"
6. Configurar rango de fechas que incluya la factura
7. Verificar que aparece 1 registro en la vista previa
8. Generar exportación
9. Verificar el archivo TXT descargado tiene 197 caracteres por línea

**Resultado esperado:**
```
0115/11/20250000000000000001000000010000000217078100000008264460015/11/20250100000000280000000000015/11/2025800000000003012345678900000000000000      PROVEEDOR TEST S.A.030123456789 30123456789
```

---

### Caso 2: Exportar Percepciones IIBB

**Configuración previa:**

1. **Cuenta contable:**
   - Código: `2.1.3.02`
   - Nombre: `Percepciones IIBB a Pagar`
   - Exportación SICORE: **Percepciones**

2. **Impuesto:**
   - Nombre: `Percepción IIBB 2.5%`
   - Tipo: Percepción
   - Cuenta: `2.1.3.02`
   - Código Impuesto SICORE: `[0767] Ingresos Brutos`
   - Código Régimen SICORE: `[602] Percepciones IIBB`

3. **Cliente:**
   - Nombre: `Cliente Test S.R.L.`
   - Tipo Identificación: `CUIT`
   - CUIT: `30-98765432-1`

**Pasos de prueba:**

1. Crear una factura de cliente por $200.000
2. Aplicar percepción IIBB 2.5% → Percepción: $5.000
3. Publicar la factura
4. Ir a `Contabilidad > SICORE > Exportar SICORE`
5. Seleccionar "Percepciones"
6. Generar exportación
7. Verificar el archivo TXT tiene 144 caracteres por línea

**Resultado esperado:**
```
0115/11/2025000000000000000200000002050000076760210000001652892515/11/2025010000000050000000000000000000008000000000030987654321 00000000000000
```

---

### Caso 3: Exportar Combustibles

**Configuración previa:**

1. **Cuenta contable:**
   - Código: `6.1.4.01`
   - Nombre: `Combustibles`
   - Exportación SICORE: **Combustibles**

2. **Proveedor de combustible:**
   - Nombre: `YPF S.A.`
   - Tipo Identificación: `CUIT`
   - CUIT: `30-54678901-2`

3. **Empresa (configuración):**
   - CUIT configurado en la empresa

**Pasos de prueba:**

1. Crear factura de compra de combustible por $50.000
2. Imputar a la cuenta `6.1.4.01`
3. Publicar la factura
4. Ir a `Contabilidad > SICORE > Exportar SICORE`
5. Seleccionar "Combustibles"
6. Generar exportación
7. Verificar formato CSV con punto y coma

**Resultado esperado:**
```
C;YPF S.A.;30546789012;5;001;0000000001;15112025;MI EMPRESA S.R.L.;30707753303;3;50000,00
```

---

### Caso 4: Filtrar por Régimen de Partner

**Objetivo:** Exportar solo retenciones de proveedores monotributistas

**Pasos:**

1. Configurar proveedor con Régimen SICORE: `Régimen Simplificado`
2. Ir al wizard de exportación
3. Seleccionar Régimen: `Régimen Simplificado`
4. Verificar que solo aparecen proveedores monotributistas en la vista previa

---

### Caso 5: Excluir Diarios de Presupuesto

**Objetivo:** Verificar que los asientos de presupuesto no se exportan

**Pasos:**

1. Crear diario "Presupuestos" con Tipo Exportación SICORE: `Presupuestos`
2. Crear asiento en ese diario con cuenta de retención
3. Ir al wizard de exportación
4. Verificar que el asiento de presupuesto NO aparece en la vista previa

---

## Logs de Exportación

Cada exportación genera un registro de log accesible desde:

**Ruta:** `Contabilidad > SICORE > Logs de Exportación`

### Información del Log:

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Identificador de la exportación |
| **Tipo** | Retenciones / Percepciones / Combustibles |
| **Período** | Rango de fechas exportado |
| **Registros** | Cantidad de registros exportados |
| **Estado** | Éxito / Advertencia / Error |
| **Archivo** | Archivo TXT descargable |
| **Errores** | Detalle de errores si los hubo |

---

## Solución de Problemas

### Error: "No se encontró código de impuesto SICORE"

**Causa:** El impuesto aplicado no tiene configurado el campo "Código Impuesto SICORE"

**Solución:** 
1. Ir a `Contabilidad > Configuración > Impuestos`
2. Editar el impuesto de retención/percepción
3. Completar el campo "Código Impuesto SICORE"

---

### Error: "No se encontró código de régimen SICORE"

**Causa:** El impuesto aplicado no tiene configurado el campo "Código Régimen SICORE"

**Solución:** 
1. Ir a `Contabilidad > Configuración > Impuestos`
2. Editar el impuesto
3. Completar el campo "Código Régimen SICORE"

---

### Error: "El partner no tiene CUIT configurado"

**Causa:** El contacto no tiene número de identificación fiscal

**Solución:**
1. Ir al contacto en `Contactos`
2. En la pestaña "Ventas y Compras"
3. Completar "Tipo de Identificación" (CUIT) y "Nro. Identificación"

---

### Error: "El partner no tiene tipo de documento SICORE configurado"

**Causa:** El tipo de identificación del contacto no tiene mapeo SICORE

**Solución:**
1. Verificar que el tipo de identificación sea CUIT o CUIL
2. Si usa otro tipo, contactar al administrador para agregar el mapeo

---

### No aparecen registros en la vista previa

**Posibles causas:**

1. **Las cuentas no tienen configurado "Exportación SICORE"**
   - Verificar que la cuenta contable del apunte tenga el tipo correcto

2. **El diario está marcado como "Presupuestos"**
   - Verificar configuración del diario

3. **El rango de fechas no incluye los asientos**
   - Ajustar fechas en el wizard

4. **Los asientos no están publicados**
   - Solo se exportan asientos en estado "Publicado"

---

## Catálogos SICORE

### Administrar Catálogos

**Ruta:** `Contabilidad > SICORE > Configuración`

- **Códigos de Impuesto:** Lista de impuestos AFIP
- **Códigos de Régimen:** Lista de regímenes por tipo de operación
- **Tipos de Documento:** Mapeo de tipos de identificación a códigos SICORE

> **Nota:** Los catálogos se cargan automáticamente al instalar el módulo. Solo agregue nuevos registros si AFIP actualiza los códigos oficiales.

---

## Grupos de Seguridad

| Grupo | Permisos |
|-------|----------|
| **SICORE / Usuario** | Ver logs, ejecutar exportaciones |
| **SICORE / Administrador** | Todo lo anterior + editar catálogos |

---

## Soporte Técnico

Para reportar errores o solicitar nuevas funcionalidades, contactar al equipo de desarrollo UTN.

### Información del Módulo

- **Versión:** 1.0.0
- **Compatibilidad:** Odoo 18.0
- **Licencia:** LGPL-3
- **Autor:** UTN

---

## Changelog

### v1.0.0 (Diciembre 2025)
- Versión inicial
- Soporte para Retenciones (197 chars, 21 campos)
- Soporte para Percepciones (144 chars, 17 campos)
- Soporte para Combustibles (CSV, 11 campos)
- Catálogos SICORE precargados
- Logs de exportación con trazabilidad
