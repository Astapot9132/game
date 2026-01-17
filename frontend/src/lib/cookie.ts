export function getCookie(name: string): string | null {
    const entries = document.cookie ? document.cookie.split('; ') : [];
    const target = entries.find((row) => row.startsWith(`${name}=`));
    return target ? decodeURIComponent(target.split('=')[1]) : null;
  }