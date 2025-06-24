import AdminLayout from "../components/AdminLayout";
import { Providers } from "../providers";

export default function AdminSectionLayout({ children }: { children: React.ReactNode }) {
  return <AdminLayout><Providers>{children}</Providers></AdminLayout>;
}