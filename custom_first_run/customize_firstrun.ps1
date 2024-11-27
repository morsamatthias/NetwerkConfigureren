# Stap 1: Vind firstrun.sh
$firstrunPath = "./firstrun.sh"

if (Test-Path $firstrunPath) {
    Write-Output "Gevonden firstrun.sh locatie: $firstrunPath"
} else {
    Write-Output "firstrun.sh bestand niet gevonden."
    exit 1  # Exit als firstrun.sh niet gevonden is
}

# Stap 2: Lees de inhoud van firstrun.sh
$firstrunContent = Get-Content -Path $firstrunPath

# Check of de nieuwe configuratie al aanwezig is om dubbele invoer te voorkomen
$newConfigIdentifier = "[connection]"  # Een unieke identificator uit de configuratie

if ($firstrunContent -join "`n" -match [regex]::Escape($newConfigIdentifier)) {
    Write-Output "Configuratie bestaat al in firstrun.sh. Geen toevoeging nodig."
    exit 0
}

# Stap 3: Zoek naar de regel met "rm -f /boot/firstrun.sh"
$index = $firstrunContent.IndexOf("rm -f /boot/firstrun.sh")

if ($index -ge 0) {
    # Inhoud om toe te voegen
    $newConfig = @"

cat >/etc/NetworkManager/system-connections/MCT_APIPA.nmconnection <<'Static-Ip'
[connection]
id=Static_IP
type=ethernet
interface-name=eth0

[ethernet]

[ipv4]
address1=192.168.88.2/24,192.168.88.1
dns=172.20.4.140;172.20.4.141;
method=manual

[ipv6]
addr-gen-mode=default
method=auto

[proxy]
Static-Ip

chmod 0600 /etc/NetworkManager/system-connections/*
chown root:root /etc/NetworkManager/system-connections/*

"@

    # Splits de inhoud op, voeg de nieuwe inhoud toe en combineer alles
    $updatedContent = $firstrunContent[0..($index - 1)] + $newConfig + $firstrunContent[$index..($firstrunContent.Length - 1)]

    # Sla de gewijzigde inhoud op in firstrun.sh
    Set-Content -Path $firstrunPath -Value $updatedContent -Force
    Write-Output "De configuratie is toegevoegd aan $firstrunPath"
} else {
    Write-Output "De regel 'rm -f /boot/firstrun.sh' is niet gevonden in firstrun.sh"
}
