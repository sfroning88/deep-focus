import {
  Prisma,
  type TrainingFeature as PrismaTrainingFeature,
  type TrainingBatch as PrismaTrainingBatch,
  type TrainingModel as PrismaTrainingModel,
  TrainingType,
  TrainingStatus,
} from "@focus/db";

export type { TrainingType, TrainingStatus };

export type TrainingFeature = PrismaTrainingFeature;
export type TrainingBatch = PrismaTrainingBatch;
export type TrainingModel = PrismaTrainingModel;

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
