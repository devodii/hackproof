import { useQuery } from "@tanstack/react-query";
import { Table, Link } from "@/components/ui";
import { fetchApi } from "@/lib/api";

interface ErrorEntry {
  code: string;
  category: string;
  plain_english: string;
  common_cause: string;
  fix: string;
  docs_url: string;
  count: number;
}

export default function ErrorsPage() {
  const { data } = useQuery({
    queryKey: ["errorTaxonomy"],
    queryFn: () => fetchApi("/errors"),
  });

  const errors = data?.errors || [];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Soroban Error Taxonomy</h1>
      <Table>
        <Table.Header>
          <Table.Row>
            <Table.Head>Code</Table.Head>
            <Table.Head>Category</Table.Head>
            <Table.Head>Plain English</Table.Head>
            <Table.Head>Common Cause</Table.Head>
            <Table.Head>Fix</Table.Head>
            <Table.Head>Docs</Table.Head>
            <Table.Head>Occurrences</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {errors.map((error: ErrorEntry) => (
            <Table.Row key={error.code}>
              <Table.Cell>
                <Link href={`/errors/${error.code}`} className="font-mono">
                  {error.code}
                </Link>
              </Table.Cell>
              <Table.Cell>{error.category}</Table.Cell>
              <Table.Cell>{error.plain_english}</Table.Cell>
              <Table.Cell>{error.common_cause}</Table.Cell>
              <Table.Cell>{error.fix}</Table.Cell>
              <Table.Cell>
                <Link href={error.docs_url} target="_blank" rel="noopener">
                  Docs →
                </Link>
              </Table.Cell>
              <Table.Cell>{error.count}</Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </div>
  );
}
