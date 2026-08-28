import './globals.css';

export const metadata = {
  title: 'PCNA',
  description: 'PCNA sales workspace',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
