import {
  Prisma,
  type TrainingFeature as PrismaTrainingFeature,
  type TrainingSplit as PrismaTrainingSplit,
  type TrainingBatch as PrismaTrainingBatch,
  type TrainingModel as PrismaTrainingModel,
  TrainingType,
  TrainingStatus,
  TrainingFunction,
} from "@focus/db";

export type { TrainingType, TrainingStatus, TrainingFunction };

export type TrainingFeature = PrismaTrainingFeature;
export type TrainingSplit = PrismaTrainingSplit;
export type TrainingBatch = PrismaTrainingBatch;
export type TrainingModel = PrismaTrainingModel;

export type TrainingFunctionCounts = {
  train: number;
  validate: number;
  test: number;
  unassigned: number;
};

export type TrainingBatchListEntry = Prisma.TrainingBatchGetPayload<{
  include: {
    models: {
      select: {
        type: true;
        status: true;
        r2score: true;
        winner: true;
      };
    };
  };
}>;
