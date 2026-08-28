import axios from "axios";
import { api, ApiError } from "./api";

jest.mock("axios", () => {
  const mockGet = jest.fn();
  return {
    create: jest.fn(() => ({
      get: mockGet,
      post: jest.fn(),
    })),
    isAxiosError: jest.fn((err) => err && err.isAxiosError === true),
    default: {
      create: jest.fn(() => ({ get: mockGet, post: jest.fn() })),
    },
  };
});

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe("API Client - getEvaluationMetrics", () => {
  let mockGet: jest.Mock;

  beforeEach(() => {
    mockGet = (mockedAxios.create() as any).get;
    mockGet.mockClear();
  });

  it("1. 200 -> returns real metrics", async () => {
    const mockData = { total_scenarios: 1000 };
    mockGet.mockResolvedValueOnce({ data: mockData });

    const result = await api.getEvaluationMetrics();
    expect(result).toEqual(mockData);
  });

  it("2. 404 Final evaluation not found -> NO_DATA_YET error", async () => {
    const errorResponse = {
      isAxiosError: true,
      response: {
        status: 404,
        data: { detail: "Final evaluation not found" },
      },
    };
    mockGet.mockRejectedValueOnce(errorResponse);

    await expect(api.getEvaluationMetrics()).rejects.toMatchObject(
      new ApiError("NO_DATA_YET", "Final evaluation not found")
    );
  });

  it("3. 500 -> server error -> API_ERROR", async () => {
    const errorResponse = {
      isAxiosError: true,
      response: {
        status: 500,
        data: { detail: "Internal Server Error" },
      },
    };
    mockGet.mockRejectedValueOnce(errorResponse);

    await expect(api.getEvaluationMetrics()).rejects.toMatchObject(
      new ApiError("API_ERROR", "ReconAI encountered a temporary server error.")
    );
  });

  it("4. network error -> CONNECTION_ERROR", async () => {
    const errorResponse = {
      isAxiosError: true,
      // No response object
    };
    mockGet.mockRejectedValueOnce(errorResponse);

    await expect(api.getEvaluationMetrics()).rejects.toMatchObject(
      new ApiError("CONNECTION_ERROR", "Unable to reach the ReconAI backend.")
    );
  });
});


