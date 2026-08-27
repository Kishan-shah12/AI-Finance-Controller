import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Read from the backend's evaluation directory
    const filePath = path.resolve(process.cwd(), '../backend/evaluation/final/exception_report.json');
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: 'Exception report not found' }, { status: 404 });
    }
    
    const fileContents = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(fileContents);
    
    // Assign mock IDs for display purposes since the raw JSON might not have them
    const formattedData = data.map((item: any, index: number) => ({
      ...item,
      id: `EX-${1000 + index}`,
    }));
    
    return NextResponse.json(formattedData);
  } catch (error) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
