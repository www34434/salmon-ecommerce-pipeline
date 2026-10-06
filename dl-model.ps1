$target = "<本地路径>\mall-ai-service\models\embedding\bge-small-zh-v1.5"
$ip = "160.16.86.14"
$files = @("model_optimized.onnx","config.json","tokenizer.json","tokenizer_config.json","special_tokens_map.json")
# Trust all certs for IP-based HTTPS (cert is for hf-mirror.com)
add-type @"
using System.Net; using System.Security.Cryptography.X509Certificates;
public class TrustAll : System.Net.ICertificatePolicy {
    public bool CheckValidationResult(System.Net.ServicePoint sp, X509Certificate cert, System.Net.WebRequest req, int problem) { return true; }
}
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAll
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# 直连绕过 DNS 污染：hf-mirror.com 真实 IP + Host 头
foreach ($f in $files) {
    $url = "https://$ip/Qdrant/bge-small-zh-v1.5/resolve/main/$f"
    $out = Join-Path $target $f
    try {
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("Host", "hf-mirror.com")
        $wc.Headers.Add("User-Agent", "Mozilla/5.0")
        $wc.DownloadFile($url, $out)
        Write-Host "OK $f ($([math]::Round((Get-Item $out).Length/1KB))KB)"
    } catch {
        Write-Host "FAIL $f : $($_.Exception.Message)"
    }
}
