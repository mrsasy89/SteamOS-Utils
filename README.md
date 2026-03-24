# Command line tool for automating customization and configuration of handhelds & PCs running SteamOS

> **Fork** di [InnoVision-Games/SteamOS-Utils](https://github.com/InnoVision-Games/SteamOS-Utils)  
> **Modifiche**: rimozione della whitelist statica delle versioni kernel, sostituita con rilevamento dinamico e verifica live sul mirror ufficiale Valve.

---

## Differenze rispetto all'originale

Il problema principale dell'implementazione originale era una **whitelist statica** delle versioni kernel supportate.
Dopo ogni aggiornamento di SteamOS, il kernel veniva aggiornato e lo script usciva con:

```
Attempting to install on an unsupported SteamOS version, now exiting!
```

Questa fork risolve il problema in modo permanente:

| Comportamento | Originale | Questa fork |
|---|---|---|
| Versioni supportate | Whitelist statica hardcoded | Qualsiasi versione con pacchetti su mirror Valve |
| Verifica disponibilità pacchetti | No | Sì, controllo live sul mirror |
| Verifica se già installato | No | Sì, controlla `lsmod` prima di procedere |
| Messaggio di errore | Generico "unsupported version" | Indica il pacchetto mancante e il motivo |

---

## Enabling Linux Dynamic Kernel Module Support ACPI calls

In order to enable custom fan curves and setting the Legion Go charge limit we need to enable
DKMS ACPI call support for SteamOS.

In order to enable the ACPI calls the following needs to happen:

- Disable SteamOS read-only mode
- Automatically detect the current kernel version
- Check live on the official Valve mirror if the required packages exist
- Download and install the required kernel modules and kernel header packages
- Install the packages that enable the various daemons required for ACPI calls
- Re-enable SteamOS read-only mode

This script automates all of the above with a single command.

### Installazione

```bash
git clone https://github.com/mrsasy89/SteamOS-Utils.git
cd SteamOS-Utils
./SteamOsUtils.py --enable_acpi_calls
```

The command will take several minutes to run depending on your internet connection.

### Output atteso

Lo script mostrerà i seguenti step:

```
Step 1: Checking if acpi_call is already active...
Step 2: Detecting current kernel version...
Step 3: Checking package availability on Valve mirror...
  -> Package found on mirror!
  -> Package found on mirror!
All packages found on mirror! Proceeding with installation...
...
Congratulations! ACPI calls enabled. You can now use custom fan curves and charge limit!
Please reboot your device to complete the installation.
```

### Se i pacchetti non sono ancora disponibili

Se Valve non ha ancora pubblicato i pacchetti per il kernel corrente, lo script mostrerà:

```
ERROR: Kernel modules package not found on Valve mirror.
Package needed: linux-neptune-XXX-X.XX.XX.valveXX-X-x86_64.pkg.tar.zst
This SteamOS version may not yet be supported. Please check later or open an issue.
```

In questo caso attendere che Valve pubblichi i pacchetti sul mirror e riprovare.

### Verifica installazione

Dopo il riavvio, verificare che il modulo sia attivo:

```bash
dkms status
```

Output atteso:

```
acpi_call/1.2.2, 6.16.12-valve13-1-neptune-616-g324b4c971758, x86_64: installed
```

```bash
lsmod | grep acpi_call
```

### Check stato ACPI calls

```bash
./SteamOsUtils.py --check_dkms_acpi_calls_enabled
```

---

## Compatibilità testata

| Kernel | Versione Valve | SteamOS | Stato |
|---|---|---|---|
| 6.11.11 | valve27-1 | 3.7.x | ✅ Testato |
| 6.16.12 | valve13-1 | 3.8.x | ✅ Testato |

---

## Note

- Lo script è pensato per **Lenovo Legion Go** su SteamOS ma può funzionare su qualsiasi handheld con kernel Neptune.
- Dopo ogni aggiornamento SteamOS è necessario rieseguire lo script poiché il filesystem viene riscritto.
- I pacchetti kernel vengono eliminati automaticamente dopo l'installazione.
