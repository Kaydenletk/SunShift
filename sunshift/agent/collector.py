import psutil


class MetricsCollector:
    def collect(self) -> dict:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return {
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "disk_percent": disk.percent,
            "network_bytes_sent": net.bytes_sent,
            "network_bytes_recv": net.bytes_recv,
            "estimated_power_watts": self._estimate_power(cpu),
        }

    def _estimate_power(self, cpu_percent: float) -> float:
        idle_watts = 30
        max_watts = 120
        return idle_watts + (max_watts - idle_watts) * (cpu_percent / 100)
